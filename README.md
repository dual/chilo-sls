# 🐍 chilo-sls

<p align="center">
  <a href="https://chiloproject.io"><img src="https://raw.githubusercontent.com/dual/chilo-docs/main/img/logo-no-bg.png" alt="Chilo"></a>
</p>
<p align="center">
    <em>Serverless-first routing and validation that mirrors Chilo’s interfaces so you can graduate to Chilo with minimal churn.</em>
</p>

chilo-sls is a lightweight, opinionated Lambda/API Gateway framework. It auto-routes from your handler tree (glob/default `**/*.py`), applies OpenAPI or decorator-based validation, and keeps middleware/hooks consistent with Chilo so you can move from serverless to serverful when you’re ready.

---

Agents: start with [.agents/AGENTS.md](.agents/AGENTS.md) for a quick “how to use” guide.

## 📦 Install (Python 3.12)

```bash
pip install -e .
# or with pipenv
pipenv install --dev
# or with poetry
poetry install
# or with hatch
hatch env create && hatch run pip install -e .
# or with uv
uv pip install -e .
```

---

## 🎯 Why chilo-sls

- 🪂 **Serverless now, Chilo later** – Handler signatures, requirements, and validation flags align with Chilo to ease migration.
- 🗺️ **Routing without ceremony** – Point at a directory and it discovers handlers (defaults to recursive `**/*.py`) with sensible dynamic segment mapping, no mode switching.
- ✅ **Built-in validation** – Use `openapi_validate_request/response` with an OpenAPI file or requirement decorators.
- 🔌 **Lifecycle-aware middleware** – Hooks for auth, per-request work, error/timeout handling, and app lifecycle (`warmup`/`cooldown`) so you can wire observability and setup/teardown cleanly.
- 🛡️ **CORS + compression** – Response helpers for CORS and optional gzip/base64 for API Gateway.

---

## 🚀 Quick Start (API Gateway)

1) **Create a router**
```python
# api/main.py
from chilo_sls.apigateway.router import Router
from tests.mocks.apigateway import mock_middleware  # swap with your own

router = Router(
    base_path='unit-test/v1',
    handlers='api/handlers/**/*.py',      # glob or directory (defaults to **/*.py)
    openapi='api/openapi.yml',            # optional
    openapi_validate_request=True,
    openapi_validate_response=False,
    when_auth_required=mock_middleware.mock_when_auth_required,
    before_all=mock_middleware.mock_before_all,
    after_all=mock_middleware.mock_after_all,
    on_startup=[lambda: print("warm")]    # called via router.warmup()
)
```

2) **Write a handler**
```python
# api/handlers/basic.py  ->  /unit-test/v1/basic
from chilo_sls.apigateway.request import Request
from chilo_sls.apigateway.response import Response
from chilo_sls.apigateway.requirements import requirements

@requirements(required_body='v1-basic')  # matches OpenAPI schema id
def post(request: Request, response: Response) -> Response:
    response.body = {'echo': request.body}
    return response
```

3) **Call the router from your Lambda entrypoint**
```python
# lambda_handler.py
from api.main import router

# eager-load handlers and run startup hooks outside the handler
router.auto_load()
router.warmup()

def handler(event, context):
    return router.route(event, context)
```

### Dynamic routes by filename
```
api/handlers
├── __init__.py             -> /unit-test/v1/
├── user/_user_id.py        -> /unit-test/v1/user/{user_id}
└── orders/_order_id/item.py-> /unit-test/v1/orders/{order_id}/item
```

---

## 🔄 Moving up to Chilo

- Keep your handler signatures (`Request`, `Response`) and `requirements` decorators.
- Keep `when_auth_required`, `before_all`, `after_all`, `on_error`, `on_timeout`, `on_startup`, `on_shutdown`.
- Swap the runtime: chilo-sls uses Lambda events; Chilo uses WSGI/gRPC but similar routing/validation semantics.

---

## 🧪 Testing

```bash
pipenv run pytest --maxfail=20 --disable-warnings
```

---

## 📜 License

Apache 2.0 (see LICENSE).
