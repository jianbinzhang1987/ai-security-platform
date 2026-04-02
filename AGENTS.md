# Repository Guidelines

## Project Structure & Module Organization
- `client/` contains the Go CLI (`agentsec-cli`) and the Python SDK (`agentsec-python-sdk`) with their own build and test folders.
- `server/RuoYi` is the Spring Boot backend (modules `ruoyi-admin`, `ruoyi-framework`, `ruoyi-system`, `ruoyi-quartz`, `ruoyi-generator`, `ruoyi-common`) plus `sql/` schemas, `bin/` helpers, and `server/RuoYi-Vue3` for the Element Plus/Vite UI.
- `third_party/` stores OpenTelemetry snapshots, while 设计文档/ and 过程文档/ capture architecture, requirements, and process notes.

## Build, Test, and Development Commands
- `cd server/RuoYi && mvn clean install` (add `-DskipTests=true` when you only need a package); run `server/RuoYi/bin/run.bat` or `server/RuoYi/ry.sh start` to launch `ruoyi-admin.jar` with the stock JVM options.
- `cd server/RuoYi-Vue3 && npm install` then `npm run dev` for local UI work, `npm run build:prod` for release builds, and `npm run preview` to check the production bundle.
- `cd client/agentsec-cli && make build` compiles the CLI binary; `make test` runs `go test ./...` and should follow `go fmt ./...` for formatting.
- `cd client/agentsec-python-sdk && python -m pip install -e .` installs the SDK; use `pytest tests/unit` for fast feedback and extend to `tests/integration` before merging.

## Coding Style & Naming Conventions
- Java sources under `server/RuoYi` use Allman braces with four-space indentation, `com.ruoyi.*` packages, `Service`/`Mapper` suffixes, and uppercase `SNAKE_CASE` constants (see `ruoyi-common`).
- Go code in `client/agentsec-cli/cmd` follows gofmt (tabs) and cobra conventions; export only what is needed for the command tree.
- Python relies on `pydantic` models in `agentsec/`, uses snake_case identifiers, and keeps business logic separate from fixtures under `tests/`.
- Vue 3 files under `server/RuoYi-Vue3/src/{components,views}` mirror PascalCase filenames, import shared `router`, `store`, and `assets` modules, and reuse Element Plus styling from `main.js`.

## Testing Guidelines
- Java tests (when added) live under `server/RuoYi/**/src/test/java`; rely on Maven defaults so `mvn test` picks up `*Test` or `*IT` classes and document dataset wiring in `sql/`.
- Go coverage comes from `make test`, which drives `go test ./...`; add helper structs in `cmd/` only when necessary.
- Python tests are split into `tests/unit`, `tests/integration`, and `tests/fixtures`; keep fixtures aligned with `agentsec` models and re-run `pytest tests/unit` locally.
- UI verification is currently manual; use `npm run dev` to spot-check pages and capture screenshots when recording regressions.

## Commit & Pull Request Guidelines
- Keep commits imperative and scoped (for example `client: add register flag`), cite the affected layer, and mention the commands or tests you executed.
- PRs should outline the motivation, link any relevant 设计文档/ entry, describe the coverage, and attach screenshots or `npm run preview` output for UI work.

## Security & Configuration Tips
- Reload the schema with `server/RuoYi/sql/ruoyi.sql` or `ry_20260319.sql` after structural changes and keep secrets out of the tracked `.env.*` files.
- Stick to the provided JVM settings in `server/RuoYi/ry.sh` and `server/RuoYi/bin/run.bat` to mirror production runtime conditions.
- Treat `third_party/opentelemetry-*` folders as read-only references; update them by pulling from the upstream repos instead of editing them in place.
