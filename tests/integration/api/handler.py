import os
import sys

# Resolve project root from this file's location and ensure it is on sys.path and is the working directory
_here = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(_here, '..', '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

PATTERN_HANDLERS = 'tests/integration/api/pattern_handlers/**/*_controller.py'
DIRECTORY_HANDLERS = 'tests/integration/api/directory_handlers'

from chilo_sls.apigateway.router import Router
from tests.integration.api.middleware import mock_middleware


def _build_router(base_path, handlers):
    router = Router(
        base_path=base_path,
        handlers=handlers,
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
    router.auto_load()
    router.warmup()
    return router


# v2 (httpApi) routers
pattern_router = _build_router('integration/pattern', PATTERN_HANDLERS)
directory_router = _build_router('integration/directory', DIRECTORY_HANDLERS)

# v1 (http/REST API) routers
pattern_router_v1 = _build_router('integration-v1/pattern', PATTERN_HANDLERS)
directory_router_v1 = _build_router('integration-v1/directory', DIRECTORY_HANDLERS)


def pattern_handler(event, context):
    return pattern_router.route(event, context)


def directory_handler(event, context):
    return directory_router.route(event, context)


def pattern_handler_v1(event, context):
    return pattern_router_v1.route(event, context)


def directory_handler_v1(event, context):
    return directory_router_v1.route(event, context)
