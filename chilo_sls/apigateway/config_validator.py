from chilo_sls.apigateway.exception import ApiException


class ConfigValidator:

    @staticmethod
    def validate(**kwargs):
        ConfigValidator._validate_base_and_handlers(kwargs)
        ConfigValidator._validate_schema(kwargs)
        ConfigValidator._validate_openapi_flags(kwargs)
        ConfigValidator._validate_cache(kwargs)
        ConfigValidator._validate_verbose(kwargs)
        ConfigValidator._validate_hooks(kwargs)

    @staticmethod
    def _validate_base_and_handlers(kwargs):
        if not kwargs.get('base_path') or not isinstance(kwargs.get('base_path'), str):
            raise ApiException(code=500, message='base_path string is required')
        if not kwargs.get('handlers') or not isinstance(kwargs.get('handlers'), str):
            raise ApiException(code=500, message='handlers is required; must be glob pattern string')

    @staticmethod
    def _validate_schema(kwargs):
        schema_val = kwargs.get('openapi') if 'openapi' in kwargs else kwargs.get('schema')
        if schema_val and not isinstance(schema_val, (str, dict)):
            raise ApiException(code=500, message='openapi should either be file path string or json-schema style dictionary')

    @staticmethod
    def _validate_openapi_flags(kwargs):
        if kwargs.get('openapi_validate_request') and not isinstance(kwargs.get('openapi_validate_request'), bool):
            raise ApiException(code=500, message='openapi_validate_request should be a boolean')
        if kwargs.get('openapi_validate_response') and not isinstance(kwargs.get('openapi_validate_response'), bool):
            raise ApiException(code=500, message='openapi_validate_response should be a boolean')

    @staticmethod
    def _validate_cache(kwargs):
        cache_size = kwargs.get('cache_size')
        if cache_size and not isinstance(cache_size, int) and cache_size is not None:
            raise ApiException(code=500, message='cache_size should be an int (0 for unlimited size) or None (to disable route caching)')

        cache_mode = kwargs.get('cache_mode')
        if cache_mode and cache_mode not in ('all', 'static-only', 'dynamic-only'):
            raise ApiException(code=500, message='cache_mode should be a string of the one of the following values: all, static-only, dynamic-only')

    @staticmethod
    def _validate_verbose(kwargs):
        if kwargs.get('verbose') and not isinstance(kwargs.get('verbose'), bool):
            raise ApiException(code=500, message='verbose should be a boolean')

    @staticmethod
    def _validate_hooks(kwargs):
        for hook_key in ('on_startup', 'on_shutdown'):
            hooks = kwargs.get(hook_key)
            if hooks is None:
                continue
            if not isinstance(hooks, (list, tuple)):
                raise ApiException(code=500, message=f'{hook_key} should be a list or tuple of callables')
            for hook in hooks:
                if not callable(hook):
                    raise ApiException(code=500, message=f'all items in {hook_key} must be callable')
