# Backend App (Maven Consumer)

This app validates consuming the Java package from the remote Maven repository.

The app exposes:
- `GET /add?a=<int>&b=<int>`: calls foundation SWIG docs API `MarkdownDocumentApi.add(a, b)`.
- `GET /foundation/network/get?url=...&params=...`: backend -> foundation -> conan bridge network GET.
- `POST /foundation/network/post?url=...`: backend -> foundation -> conan bridge network POST.
- `GET /foundation/echo-get?msg=...` and `POST /foundation/echo-post`: local echo endpoints for network bridge self-test.

## Prerequisites

- `com.ty:native-spring-server-bridge:0.1.2` and companion modules are already published to `maven-releases`.
- Maven credentials for `maven-releases` are configured in `~/.m2/settings.xml`.
- foundation SWIG docs JNI library is built first (`cd Library && invoke app-foundation` or `cd Library && invoke app-backend`).

## Run

Preferred invoke workflow:

```bash
cd App/backend
invoke deps
invoke build
```

Or from App root:

```bash
cd App
invoke build
```

Direct Maven run:

```bash
cd App/backend
mvn -U spring-boot:run
# then in another terminal:
curl "http://127.0.0.1:8080/add?a=7&b=5"
curl "http://127.0.0.1:8080/foundation/network/get?url=http://127.0.0.1:8080/foundation/echo-get&params=msg%3Dhello"
curl -X POST "http://127.0.0.1:8080/foundation/network/post?url=http://127.0.0.1:8080/foundation/echo-post" -d "hello-post"
```

Expected response:

- `{"a":7,"b":5,"result":12}`
