# Backend App (Maven Consumer)

This app validates consuming the Java package from the remote Maven repository.

The app exposes:
- `GET /add?a=<int>&b=<int>`: calls foundation SWIG math API `MathApi.add(a, b)`.
- Logs request/result via `CloudLoggerRegistry.upload(...)` (from Maven log library).

## Prerequisites

- `com.ty:native-spring-server-bridge:0.2.8` is already published to `maven-releases`.
- Maven credentials for `maven-releases` are configured in `~/.m2/settings.xml`.
- foundation SWIG math JNI library is built first (`cd Library && invoke app-foundation` or `cd Library && invoke app-backend`).

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
```

Expected response:

- `{"a":7,"b":5,"result":12}`
