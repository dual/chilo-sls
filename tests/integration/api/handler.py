import glob
import os
import sys

# Resolve project root from this file's location and ensure it is on sys.path and is the working directory
_here = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(_here, '..', '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

PATTERN_HANDLERS = os.path.join('tests', 'integration', 'api', 'pattern_handlers', '**', '*_controller.py')
DIRECTORY_HANDLERS = os.path.join('tests', 'integration', 'api', 'directory_handlers')

print(f'[DEBUG] __file__={__file__}', flush=True)
print(f'[DEBUG] _here={_here}', flush=True)
print(f'[DEBUG] ROOT_DIR={ROOT_DIR}', flush=True)
print(f'[DEBUG] cwd={os.getcwd()}', flush=True)
print(f'[DEBUG] PATTERN_HANDLERS={PATTERN_HANDLERS}', flush=True)
print(f'[DEBUG] glob_result={glob.glob(PATTERN_HANDLERS, recursive=True)}', flush=True)

from chilo_sls.apigateway.router import Router
from tests.integration.api.middleware import mock_middleware


pattern_router = Router(
    base_path='integration/pattern',
    handlers=PATTERN_HANDLERS,
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
    handlers=DIRECTORY_HANDLERS,
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
    import json
    print(f'[DEBUG] event={json.dumps(event, default=str)}', flush=True)
    return pattern_router.route(event, context)


def directory_handler(event, context):
    return directory_router.route(event, context)
