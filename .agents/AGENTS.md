# AGENTS: Using chilo-sls

This library mirrors Chilo’s API surface for AWS Lambda/API Gateway. Agents: start here to integrate quickly; this is **not** a contributor guide.

## Core Concepts

- **Router**: `chilo_sls.apigateway.router.Router` takes a `base_path` and a glob `handlers` (directories default to `**/*.py`). It auto-routes based on file paths.
- **Handlers**: Regular Python modules/functions (e.g., `post`, `get`) in your handlers glob. Dynamic segments use `_` in filenames/directories (e.g., `_user_id.py` → `{user_id}`).
- **Requests/Responses**: Use `chilo_sls.apigateway.request.Request` and `chilo_sls.apigateway.response.Response`. Request wraps Lambda events; Response produces API Gateway–compatible output.
- **Requirements**: Decorators in `chilo_sls.apigateway.requirements` to attach validation metadata (e.g., `required_body`, `required_query`).
- **Validation**: Turn on `openapi_validate_request`/`openapi_validate_response` with `openapi=<path or dict>`; otherwise use requirements-only validation.
- **Hooks**: `before_all`, `after_all`, `when_auth_required`, `on_error`, `on_timeout`. Lifecycle: `on_startup`, `on_shutdown` via `router.warmup()` / `router.cooldown()`.

## Minimal Setup

```python
from chilo_sls.apigateway.router import Router

router = Router(
    base_path='v1',
    handlers='api/handlers',           # directory or glob; directory defaults to **/*.py
    openapi='api/openapi.yml',         # optional
    openapi_validate_request=True,     # optional
    openapi_validate_response=False,   # optional
    when_auth_required=auth_hook,      # optional
    before_all=before_hook,            # optional
    after_all=after_hook,              # optional
    on_startup=[init_db],              # optional
    on_shutdown=[close_db],            # optional
)
```

Lambda entrypoint:

```python
from api.main import router

def handler(event, context):
    return router.route(event, context)
```

Warm/cool (optional):

```python
def warmup(event, context):
    router.warmup()

def cooldown(event, context):
    router.cooldown()
```

## Handler Example

```python
# api/handlers/user/_user_id.py  -> /v1/user/{user_id}
from chilo_sls.apigateway.request import Request
from chilo_sls.apigateway.response import Response
from chilo_sls.apigateway.requirements import requirements

@requirements(required_body='v1-user-update')
def post(request: Request, response: Response) -> Response:
    response.body = {'id': request.path_params['user_id'], 'payload': request.body}
    return response
```

## Patterns & Tips

- Handlers glob: pass a directory to auto-expand to `**/*.py`, or pass an explicit glob.
- Dynamic params: prefix filenames/dirs with `_` (e.g., `_id.py`, `_user_id/item/_item_id.py`).
- Validation: request/response validation only runs when you set the `openapi_validate_*` flags.
- Auth: `when_auth_required` runs if OpenAPI security is present or endpoint requires_auth.
- CORS/Compression: Response sets CORS headers by default; set `response.compress = True` to gzip/base64 body.
- Cache: Router caches resolved endpoints; `cache_size=None` disables, `0` unlimited, `cache_mode` = `all|static-only|dynamic-only`.

## Parity with Chilo

- Naming: use `when_auth_required`, `before_all`, `after_all`, `on_startup`, `on_shutdown`, `openapi_validate_request/response`, `openapi`.
- Request properties: `authorization`, `content_type`, `mimetype`, `host_url`, `domain`, `method`, `path`, `route`, `path_params`, `query_params`, `body/json/form/xml/graphql/raw/text`, `cookies`, `timeout`.
- Response properties: `headers`, `cors`, `compress`, `code`, `has_errors`, `body/raw`, `content_type`, `is_json`, `base64_encoded`, `full`.
