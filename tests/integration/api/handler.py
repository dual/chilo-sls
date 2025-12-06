import os
import sys

# Ensure project root is on sys.path so chilo_sls and integration helpers resolve when run via serverless-offline
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from chilo_sls.apigateway.router import Router
from tests.integration.api.middleware import mock_middleware


pattern_router = Router(
    base_path='integration/pattern',
    handlers='tests/integration/api/pattern_handlers/**/*.py',
    openapi_validate_request=False,
    openapi_validate_response=False,
    when_auth_required=mock_middleware.mock_when_auth_required,
    before_all=mock_middleware.mock_before_all,
    after_all=mock_middleware.mock_after_all,
    on_error=mock_middleware.mock_on_error,
    on_timeout=mock_middleware.mock_on_timeout,
    on_startup=[mock_middleware.mock_on_startup],
    on_shutdown=[mock_middleware.mock_on_shutdown],
)
pattern_router.auto_load()
pattern_router.warmup()


directory_router = Router(
    base_path='integration/directory',
    handlers='tests/integration/api/directory_handlers/**/*.py',
    openapi_validate_request=False,
    openapi_validate_response=False,
    when_auth_required=mock_middleware.mock_when_auth_required,
    before_all=mock_middleware.mock_before_all,
    after_all=mock_middleware.mock_after_all,
    on_error=mock_middleware.mock_on_error,
    on_timeout=mock_middleware.mock_on_timeout,
    on_startup=[mock_middleware.mock_on_startup],
    on_shutdown=[mock_middleware.mock_on_shutdown],
)
directory_router.auto_load()
directory_router.warmup()


def pattern_handler(event, context):
    return pattern_router.route(event, context)


def directory_handler(event, context):
    return directory_router.route(event, context)
