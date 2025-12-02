import unittest

from chilo_sls.apigateway.config_validator import ConfigValidator
from chilo_sls.apigateway.exception import ApiException


class ConfigValidatorTest(unittest.TestCase):

    def test_config_validator_validates_all_passing(self):
        try:
            ConfigValidator.validate(
                base_path='some/path',
                handlers='some/path/**/*.py',
                openapi='path/to/schema',
                openapi_validate_request=True,
                openapi_validate_response=True,
                cache_size=128,
                cache_mode='all'
            )
            # alternative options
            ConfigValidator.validate(
                base_path='some/path',
                handlers='some/path',
                openapi={'json_schema': True},
                openapi_validate_request=False,
                openapi_validate_response=False,
                cache_size=None
            )
            self.assertTrue(True)
        except ApiException as api_error:
            print(api_error.message)
            self.assertTrue(False)

    def test_config_validator_validates_base_path(self):
        try:
            ConfigValidator.validate(**{})
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('base_path string is required', api_error.message)

    def test_config_validator_validates_routing_handlers_is_required(self):
        try:
            ConfigValidator.validate(base_path='some/path')
            self.assertTrue(False)
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('handlers is required; must be glob pattern string', api_error.message)

    def test_config_validator_validates_routing_handlers_are_appropriate(self):
        try:
            ConfigValidator.validate(base_path='some/path', handlers=1)
            self.assertTrue(False)
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('handlers is required; must be glob pattern string', api_error.message)

    def test_config_validator_validates_routing_schema_is_appropriate(self):
        try:
            ConfigValidator.validate(base_path='some/path', handlers='some/path/**/*.py', openapi=1)
            self.assertTrue(False)
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('openapi should either be file path string or json-schema style dictionary', api_error.message)

    def test_config_validator_validates_routing_openapi_validate_request_is_appropriate(self):
        try:
            ConfigValidator.validate(base_path='some/path', handlers='some/path/**/*.py', openapi_validate_request=1)
            self.assertTrue(False)
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('openapi_validate_request should be a boolean', api_error.message)

    def test_config_validator_validates_routing_openapi_validate_response_is_appropriate(self):
        try:
            ConfigValidator.validate(base_path='some/path', handlers='some/path/**/*.py', openapi_validate_response=1)
            self.assertTrue(False)
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('openapi_validate_response should be a boolean', api_error.message)

    def test_config_validator_validates_routing_verbose_is_appropriate(self):
        try:
            ConfigValidator.validate(base_path='some/path', handlers='some/path/**/*.py', verbose=1)
            self.assertTrue(False)
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('verbose should be a boolean', api_error.message)

    def test_config_validator_validates_routing_cache_size_is_appropriate(self):
        try:
            ConfigValidator.validate(base_path='some/path', handlers='some/path/**/*.py', cache_size='1')
            self.assertTrue(False)
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('cache_size should be an int (0 for unlimited size) or None (to disable route caching)', api_error.message)

    def test_config_validator_validates_routing_cache_mode_is_appropriate(self):
        try:
            ConfigValidator.validate(base_path='some/path', handlers='some/path/**/*.py', cache_mode='bad')
            self.assertTrue(False)
        except ApiException as api_error:
            self.assertTrue(isinstance(api_error, ApiException))
            self.assertEqual('cache_mode should be a string of the one of the following values: all, static-only, dynamic-only', api_error.message)
