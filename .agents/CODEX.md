# CODEX: Project Context & Contribution Guide

## What this project is
- **chilo-sls**: A serverless-first framework for AWS Lambda + API Gateway that mirrors Chilo’s developer ergonomics.
- **Goal**: Provide a drop-in Lambda experience that aligns with Chilo’s routing, validation, and middleware patterns so teams can graduate to Chilo with minimal refactor.

## How the code is written
- **Routing**: A single pattern resolver; directories default to `**/*.py`. Dynamic segments use `_` in filenames/dirs.
- **Validation**: Optional OpenAPI request/response validation (`openapi_validate_request/response`) plus requirement decorators.
- **Middleware/Hooks**: `before_all`, `after_all`, `when_auth_required`, `on_error`, `on_timeout`, lifecycle via `on_startup`/`on_shutdown` (invoked by `warmup()`/`cooldown()`).
- **Parallels to Chilo**: Request/Response properties, hook names, and validation flags match Chilo to ease migration.
- **Testing**: `pipenv run pytest --maxfail=20 --disable-warnings`; tests live under `tests/chilo_sls`.

## How to contribute
1) **Align with Chilo**: Keep public interfaces (kwargs, property names) consistent with Chilo unless intentionally diverging for Lambda specifics.
2) **Prefer pattern routing**: No mapping/directory modes—unified glob resolver only.
3) **Validation flags**: Use `openapi_validate_request/response` and `openapi` (schema) consistently; keep requirements decorators intact.
4) **Hooks**: Preserve hook names (`when_auth_required`, etc.) and lifecycle semantics (`warmup`/`cooldown` call `on_startup`/`on_shutdown`).
5) **Testing**: Add/adjust unit tests alongside code changes; ensure full suite passes via Pipenv. Target Python 3.12 runtime.
6) **Docs**: Update README/AGENTS when changing interfaces or workflows; avoid referencing older acai projects.
7) **Style**: Keep code minimal and explicit; avoid unnecessary abstractions; match existing naming patterns.
