from __future__ import annotations

import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from invoke import task

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Tools.invoke_support import run, success, task_scope
from Tools.project_config import (
    PROJECT_CONAN_CMD,
    DEFAULT_CONAN_REMOTE_NAME,
    DEFAULT_CONAN_REMOTE_URL,
    DEFAULT_MAVEN_RELEASES_REPO_ID,
    DEFAULT_MAVEN_RELEASES_REPO_URL,
    PROJECT_MAVEN_SETTINGS,
)

NATIVE_DIR = ROOT / "native"
NATIVE_BUILD_DIR = NATIVE_DIR / "build"
TARGET_DIR = ROOT / "target"
DIST_DIR = ROOT / "dist"
JAVA_IMPL_SRC_DIR = ROOT / "src" / "impl-java"
JAVA_IMPL_TARGET_DIR = TARGET_DIR / "generated-sources" / "cloudlogger-impl"
NATIVE_PACKAGE_INCLUDE_DIR = DIST_DIR / "native" / "include"
NATIVE_PACKAGE_LIB_DIR = DIST_DIR / "native" / "lib"
APP_FOUNDATION_DIR = REPO_ROOT / "App" / "foundation"
APP_BACKEND_DIR = REPO_ROOT / "App" / "backend"


def _rm(path: Path) -> None:
    if path.is_file() or path.is_symlink():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def _conan_ref(name: str, version: str, user: str = "", channel: str = "") -> str:
    if bool(user) != bool(channel):
        raise ValueError("`user` and `channel` must be provided together")
    ref = f"{name}/{version}"
    if user and channel:
        ref = f"{ref}@{user}/{channel}"
    return ref


def _pom_version() -> str:
    root = ET.parse(ROOT / "pom.xml").getroot()
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    version = root.findtext("m:version", namespaces=ns)
    if not version:
        raise RuntimeError("cannot read <version> from pom.xml")
    return version.strip()


def _maven_settings_arg(settings_file: str) -> str:
    return f"-s {settings_file}" if settings_file else ""


def _compile_swig_java(c) -> None:
    swig_dir = TARGET_DIR / "generated-sources" / "cloudlogger-swig"
    classes_dir = TARGET_DIR / "generated-classes" / "cloudlogger-swig"
    classes_dir.mkdir(parents=True, exist_ok=True)

    java_files = sorted(str(p) for p in swig_dir.glob("*.java"))
    if not java_files:
        raise RuntimeError("no SWIG Java sources found, run native-build first")

    _rm(classes_dir)
    classes_dir.mkdir(parents=True, exist_ok=True)

    c.run(f"javac --release 21 -d {classes_dir} " + " ".join(java_files), pty=True)


def _compile_impl_java(c, mvn_cmd: str = "mvn", settings_file: str = PROJECT_MAVEN_SETTINGS) -> None:
    impl_src_dir = TARGET_DIR / "generated-sources" / "cloudlogger-impl"
    classes_dir = TARGET_DIR / "generated-classes" / "cloudlogger-impl"
    classpath_file = TARGET_DIR / "compile.classpath"

    java_files = sorted(str(p) for p in impl_src_dir.rglob("*.java"))
    if not java_files:
        raise RuntimeError("no implementation Java sources found, run java-prepare first")

    _rm(classes_dir)
    classes_dir.mkdir(parents=True, exist_ok=True)
    settings_arg = _maven_settings_arg(settings_file)
    c.run(
        (
            f"{mvn_cmd} {settings_arg} -q -DincludeScope=compile "
            f"dependency:build-classpath -Dmdep.outputFile={classpath_file}"
        ).strip(),
        pty=True,
    )
    dep_cp = classpath_file.read_text(encoding="utf-8").strip()
    swig_cp = TARGET_DIR / "generated-classes" / "cloudlogger-swig"
    compile_cp = f"{swig_cp}:{dep_cp}" if dep_cp else str(swig_cp)
    c.run(
        f"javac --release 21 -cp {compile_cp} -d {classes_dir} " + " ".join(java_files),
        pty=True,
    )


@task
def native_clean(c):
    """Clean native build outputs."""
    with task_scope("Library native-clean"):
        _rm(NATIVE_BUILD_DIR)
        _rm(TARGET_DIR / "native")
        _rm(TARGET_DIR / "generated-sources" / "cloudlogger-swig")


@task
def native_build(c, build_type="Release", jobs=""):
    """Configure + build native bridge and SWIG bindings."""
    with task_scope("Library native-build"):
        jobs_arg = f"-j{jobs}" if jobs else "-j"
        # Force full native reconfigure + SWIG regeneration to avoid stale bindings.
        _rm(NATIVE_BUILD_DIR)
        _rm(TARGET_DIR / "generated-sources" / "cloudlogger-swig")
        run(
            c,
            f"cmake -S {NATIVE_DIR} -B {NATIVE_BUILD_DIR} -DCMAKE_BUILD_TYPE={build_type}",
            title="Configure native CMake",
        )
        run(c, f"cmake --build {NATIVE_BUILD_DIR} {jobs_arg}", title="Build native outputs")


@task
def native_package(c):
    """Package native headers and shared libraries into dist/native."""
    include_src = NATIVE_DIR / "include"
    libs_src = TARGET_DIR / "native" / "lib"

    if not libs_src.exists():
        raise RuntimeError("native libs not found, run `invoke native-build` first")

    _rm(DIST_DIR / "native")
    NATIVE_PACKAGE_INCLUDE_DIR.mkdir(parents=True, exist_ok=True)
    NATIVE_PACKAGE_LIB_DIR.mkdir(parents=True, exist_ok=True)

    for header in include_src.glob("*.hpp"):
        shutil.copy2(header, NATIVE_PACKAGE_INCLUDE_DIR / header.name)

    for lib in libs_src.glob("*.so"):
        shutil.copy2(lib, NATIVE_PACKAGE_LIB_DIR / lib.name)


@task
def java_prepare(c):
    """Copy Java implementation classes into generated-sources."""
    with task_scope("Library java-prepare"):
        _rm(JAVA_IMPL_TARGET_DIR)
        JAVA_IMPL_TARGET_DIR.mkdir(parents=True, exist_ok=True)

        if not JAVA_IMPL_SRC_DIR.exists():
            raise RuntimeError(f"missing implementation source dir: {JAVA_IMPL_SRC_DIR}")

        for src_file in JAVA_IMPL_SRC_DIR.rglob("*.java"):
            rel = src_file.relative_to(JAVA_IMPL_SRC_DIR)
            dst = JAVA_IMPL_TARGET_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst)


@task
def java_build(c, skip_tests=True, mvn_cmd="mvn", settings_file=PROJECT_MAVEN_SETTINGS):
    """Build Java artifact with generated SWIG and implementation sources."""
    with task_scope("Library java-build"):
        skip_flag = "-DskipTests" if skip_tests else ""
        settings_arg = _maven_settings_arg(settings_file)
        run(c, f"{mvn_cmd} {settings_arg} clean".strip(), title="Clean Maven outputs")
        native_build(c)
        java_prepare(c)
        _compile_swig_java(c)
        _compile_impl_java(c, mvn_cmd=mvn_cmd, settings_file=settings_file)
        run(
            c,
            (
                f"{mvn_cmd} {settings_arg} package {skip_flag} "
                "-Dmaven.compiler.useIncrementalCompilation=false"
            ).strip(),
            title="Package library jar",
        )


@task(pre=[java_build])
def java_package(c):
    """Copy jar artifact into dist/java."""
    jars = sorted((TARGET_DIR).glob("*.jar"))
    if not jars:
        raise RuntimeError("jar artifact not found, run `invoke java-build` first")

    java_dist = DIST_DIR / "java"
    _rm(java_dist)
    java_dist.mkdir(parents=True, exist_ok=True)

    for jar in jars:
        if jar.name.endswith("-sources.jar") or jar.name.endswith("-javadoc.jar"):
            continue
        shutil.copy2(jar, java_dist / jar.name)


@task(pre=[native_clean])
def clean(c):
    """Clean all build outputs."""
    _rm(TARGET_DIR)
    _rm(DIST_DIR)


@task(pre=[java_build])
def build(c):
    """Build native + java layers."""


@task(pre=[native_package, java_package])
def package(c):
    """Package native + java artifacts under dist/."""


@task
def conan_remote(
    c,
    remote=DEFAULT_CONAN_REMOTE_NAME,
    url=DEFAULT_CONAN_REMOTE_URL,
    conan_cmd=PROJECT_CONAN_CMD,
):
    """Ensure Conan remote exists (idempotent)."""
    with task_scope("Library conan-remote"):
        run(c, f"{conan_cmd} remote add {remote} {url} --force", title="Configure Conan remote")


@task
def conan_create(
    c,
    name="cloudlogger-native",
    version="0.1.0",
    user="",
    channel="",
    profile="",
    build_type="Release",
    conan_cmd=PROJECT_CONAN_CMD,
):
    """Create Conan package from local recipe."""
    with task_scope("Library conan-create"):
        ref = _conan_ref(name=name, version=version, user=user, channel=channel)
        profile_arg = f"-pr {profile}" if profile else ""
        user_arg = f"--user {user}" if user else ""
        channel_arg = f"--channel {channel}" if channel else ""
        run(
            c,
            (
                f"{conan_cmd} create . --name {name} --version {version} "
                f"{user_arg} {channel_arg} -s build_type={build_type} {profile_arg}"
            ).strip(),
            title="Create Conan package",
        )
        success(f"Conan package created: {ref}")


@task
def conan_upload(
    c,
    name="cloudlogger-native",
    version="0.1.0",
    user="",
    channel="",
    remote=DEFAULT_CONAN_REMOTE_NAME,
    conan_cmd=PROJECT_CONAN_CMD,
):
    """Upload Conan package to configured remote (package must exist locally)."""
    with task_scope("Library conan-upload"):
        ref = _conan_ref(name=name, version=version, user=user, channel=channel)
        run(c, f'{conan_cmd} upload "{ref}" -r {remote} --confirm', title="Upload Conan package")
        success(f"Conan package uploaded: {ref} -> {remote}")


@task
def conan_publish(
    c,
    name="cloudlogger-native",
    version="0.1.0",
    user="",
    channel="",
    remote=DEFAULT_CONAN_REMOTE_NAME,
    remote_url=DEFAULT_CONAN_REMOTE_URL,
    profile="",
    build_type="Release",
    conan_cmd=PROJECT_CONAN_CMD,
):
    """One-shot remote add + create + upload for Conan2 native package."""
    with task_scope("Library conan-publish"):
        ref = _conan_ref(name=name, version=version, user=user, channel=channel)
        profile_arg = f"-pr {profile}" if profile else ""
        user_arg = f"--user {user}" if user else ""
        channel_arg = f"--channel {channel}" if channel else ""

        run(c, f"{conan_cmd} remote add {remote} {remote_url} --force", title="Configure Conan remote")
        run(
            c,
            (
                f"{conan_cmd} create . --name {name} --version {version} "
                f"{user_arg} {channel_arg} -s build_type={build_type} {profile_arg}"
            ).strip(),
            title="Create Conan package",
        )
        run(c, f'{conan_cmd} upload "{ref}" -r {remote} --confirm', title="Upload Conan package")
        success(f"Conan publish done: {ref} -> {remote} ({remote_url})")


@task
def java_publish(
    c,
    repo_id=DEFAULT_MAVEN_RELEASES_REPO_ID,
    repo_url=DEFAULT_MAVEN_RELEASES_REPO_URL,
    version="",
    skip_tests=True,
    mvn_cmd="mvn",
    settings_file=PROJECT_MAVEN_SETTINGS,
):
    """
    Publish Java core library to Maven repository.

    If `version` is set, pom version will be switched temporarily for deploy and reverted afterwards.
    """
    with task_scope("Library java-publish"):
        origin_version = _pom_version()
        deploy_version = version.strip() if version else origin_version

        if deploy_version.endswith("-SNAPSHOT") and repo_id == DEFAULT_MAVEN_RELEASES_REPO_ID:
            if version:
                raise RuntimeError(
                    "maven-releases does not accept SNAPSHOT versions. "
                    "pass a release version like `--version 0.1.0`."
                )
            deploy_version = deploy_version.removesuffix("-SNAPSHOT")
            if not deploy_version:
                raise RuntimeError("invalid pom version: cannot derive release version from SNAPSHOT")
            print(
                f"Detected SNAPSHOT pom version `{origin_version}`, "
                f"auto using release version `{deploy_version}` for publish."
            )

        skip_flag = "-DskipTests" if skip_tests else ""
        deploy_repo = f"-DaltDeploymentRepository={repo_id}::default::{repo_url}"
        settings_arg = _maven_settings_arg(settings_file)

        changed = deploy_version != origin_version
        try:
            if changed:
                run(
                    c,
                    (
                        f"{mvn_cmd} {settings_arg} versions:set "
                        f"-DnewVersion={deploy_version} -DgenerateBackupPoms=false"
                    ).strip(),
                    title="Switch Maven version",
                )
            run(c, f"{mvn_cmd} {settings_arg} clean".strip(), title="Clean Maven outputs")
            native_build(c)
            java_prepare(c)
            _compile_swig_java(c)
            _compile_impl_java(c, mvn_cmd=mvn_cmd, settings_file=settings_file)
            _rm(TARGET_DIR / "classes")
            run(
                c,
                (
                    f"{mvn_cmd} {settings_arg} package {skip_flag} "
                    "-Dmaven.compiler.useIncrementalCompilation=false"
                ).strip(),
                title="Package library jar",
            )
            run(
                c,
                (
                    f"{mvn_cmd} {settings_arg} deploy {skip_flag} {deploy_repo} "
                    "-Dmaven.main.skip=true"
                ).strip(),
                title="Deploy library jar",
            )
        finally:
            if changed:
                run(
                    c,
                    (
                        f"{mvn_cmd} {settings_arg} versions:set "
                        f"-DnewVersion={origin_version} -DgenerateBackupPoms=false"
                    ).strip(),
                    title="Restore Maven version",
                )

        success(f"Maven publish done: {deploy_version} -> {repo_id} ({repo_url})")


@task(name="app-foundation", aliases=["test-foundation"])
def app_foundation(
    c,
    remote=DEFAULT_CONAN_REMOTE_NAME,
    remote_url=DEFAULT_CONAN_REMOTE_URL,
    profile="",
    build_type="Release",
    conan_cmd=PROJECT_CONAN_CMD,
):
    """Build foundation JNI library by consuming native package from Conan2 remote."""
    with task_scope("Library app-foundation"):
        profile_arg = f"-pr {profile}" if profile else ""
        run(c, f"{conan_cmd} remote add {remote} {remote_url} --force", title="Configure Conan remote")
        run(
            c,
            (
                f"cd {APP_FOUNDATION_DIR} && "
                f"{conan_cmd} install . --build=missing -r {remote} -s build_type={build_type} {profile_arg} -of build"
            ).strip(),
            title="Install foundation dependencies",
        )
        run(
            c,
            (
                f"cd {APP_FOUNDATION_DIR} && "
                "cmake -S . -B build "
                "-DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake "
                f"-DCMAKE_BUILD_TYPE={build_type}"
            ),
            title="Configure foundation CMake",
        )
        run(c, f"cd {APP_FOUNDATION_DIR} && cmake --build build -j", title="Build foundation")


@task(name="app-backend", aliases=["test-backend"])
def app_backend(
    c,
    mvn_cmd="mvn",
    settings_file=PROJECT_MAVEN_SETTINGS,
    cloudlogger_version="",
    conan_cmd=PROJECT_CONAN_CMD,
    remote=DEFAULT_CONAN_REMOTE_NAME,
    remote_url=DEFAULT_CONAN_REMOTE_URL,
):
    """Run backend app (build foundation SWIG math lib first, then start backend)."""
    with task_scope("Library app-backend"):
        run(c, f"{conan_cmd} remote add {remote} {remote_url} --force", title="Configure Conan remote")
        run(
            c,
            (
                f"cd {APP_FOUNDATION_DIR} && "
                f"{conan_cmd} install . --build=missing -r {remote} -s build_type=Release -of build"
            ),
            title="Install foundation dependencies",
        )
        run(
            c,
            (
                f"cd {APP_FOUNDATION_DIR} && "
                "cmake -S . -B build "
                "-DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake "
                "-DCMAKE_BUILD_TYPE=Release"
            ),
            title="Configure foundation CMake",
        )
        run(c, f"cd {APP_FOUNDATION_DIR} && cmake --build build -j", title="Build foundation")

        settings_arg = f"-s {settings_file}" if settings_file else ""
        version_arg = f"-Dcloudlogger.version={cloudlogger_version}" if cloudlogger_version else ""
        run(
            c,
            (f"cd {APP_BACKEND_DIR} && " f"{mvn_cmd} -U spring-boot:run {version_arg} {settings_arg}").strip(),
            title="Run backend app",
        )
