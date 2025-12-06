import unittest

from chilo_sls.apigateway.request import Request
from chilo_sls.apigateway.response import Response
from chilo_sls.apigateway.resolver.modes.pattern import PatternModeResolver
from chilo_sls.apigateway.exception import ApiException
from tests.unit.mocks.apigateway import mock_request


class PatternModeResolverTest(unittest.TestCase):
    basic_request = mock_request.get_basic()
    nested_request = mock_request.get_basic_nested()
    init_request = mock_request.get_basic_init()
    dynamic_request = mock_request.get_dynamic()
    bad_route_request = mock_request.get_bad_route()
    triple_request = mock_request.get_triple_post()
    base_path = 'unit-test/v1'
    pattern = 'tests/unit/mocks/apigateway/resolver/pattern_handlers/**/*_controller.py'
    handler_directory = 'tests/unit/mocks/apigateway/resolver/directory_handlers'
    handler_directory_no_root_init = 'tests/unit/mocks/apigateway/resolver/directory_handlers_no_root_init'
    expected_endpoint_return = {
        'hasErrors': False,
        'response': {
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*'
            },
            'statusCode': 200,
            'isBase64Encoded': False,
            'body': {
                'basic_pattern': True
            }
        }
    }

    def setUp(self):
        self.pattern_resolver = PatternModeResolver(base_path=self.base_path, handlers=self.pattern)

    def test_get_endpoint_module(self):
        request = Request(self.basic_request)
        response = Response()
        endpoint_module = self.pattern_resolver.get_endpoint_module(request)
        self.assertTrue(hasattr(endpoint_module, 'post'))
        endpoint_returns = endpoint_module.post(request, response)
        self.assertEqual(str(self.expected_endpoint_return), str(endpoint_returns))

    def test_basic_get_file_and_import_path(self):
        request = Request(self.basic_request)
        file_path, import_path = self.pattern_resolver._get_file_and_import_path(request.path)
        self.assertTrue('tests/unit/mocks/apigateway/resolver/pattern_handlers/basic/basic_controller.py' in file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.pattern_handlers.basic.basic_controller', import_path)

    def test_nested_get_file_and_import_path(self):
        request = Request(self.nested_request)
        file_path, import_path = self.pattern_resolver._get_file_and_import_path(request.path)
        self.assertTrue('tests/unit/mocks/apigateway/resolver/pattern_handlers/nested_1/nested_2/basic/basic_controller.py' in file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.pattern_handlers.nested_1.nested_2.basic.basic_controller', import_path)

    def test_default_init_get_file_and_import_path(self):
        request = Request(self.init_request)
        file_path, import_path = self.pattern_resolver._get_file_and_import_path(request.path)
        self.assertTrue('tests/unit/mocks/apigateway/resolver/pattern_handlers/home/home_controller.py' in file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.pattern_handlers.home.home_controller', import_path)

    def test_dynamic_get_file_and_import_path(self):
        request = Request(self.dynamic_request)
        file_path, import_path = self.pattern_resolver._get_file_and_import_path(request.path)
        self.assertTrue('tests/unit/mocks/apigateway/resolver/pattern_handlers/dynamic/_id_controller.py' in file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.pattern_handlers.dynamic._id_controller', import_path)

    def test_file_and_import_path_not_found_raises_resolver_exception(self):
        try:
            request = Request(self.bad_route_request)
            self.pattern_resolver._get_file_and_import_path(request.path)
            self.assertTrue(False)
        except ApiException as resolver_error:
            self.assertTrue(isinstance(resolver_error, ApiException))
            self.assertEqual(resolver_error.code, 404)
            self.assertEqual(resolver_error.message, 'route not found')

    def test_triple_dynamic_get_file_and_import_path(self):
        request = Request(self.triple_request)
        file_path, import_path = self.pattern_resolver._get_file_and_import_path(request.path)
        self.assertTrue('tests/unit/mocks/apigateway/resolver/pattern_handlers/triple/_coordinates_controller.py' in file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.pattern_handlers.triple._coordinates_controller', import_path)

    def test_single_nested_dynamic_get_file_and_import_path(self):
        dynamic_nested_request = mock_request.get_dynamic_nested_request_get('user/1')
        request = Request(dynamic_nested_request)
        file_path, import_path = self.pattern_resolver._get_file_and_import_path(request.path)
        self.assertTrue('tests/unit/mocks/apigateway/resolver/pattern_handlers/user/_user_id/_user_id_controller.py' in file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.pattern_handlers.user._user_id._user_id_controller', import_path)

    def test_double_nested_dynamic_get_file_and_import_path(self):
        dynamic_nested_request = mock_request.get_dynamic_nested_request_get('user/1/item')
        request = Request(dynamic_nested_request)
        file_path, import_path = self.pattern_resolver._get_file_and_import_path(request.path)
        self.assertTrue('tests/unit/mocks/apigateway/resolver/pattern_handlers/user/_user_id/item/item_controller.py' in file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.pattern_handlers.user._user_id.item.item_controller', import_path)

    def test_triple_nested_dynamic_get_file_and_import_path(self):
        dynamic_nested_request = mock_request.get_dynamic_nested_request_get('user/1/item/a')
        request = Request(dynamic_nested_request)
        file_path, import_path = self.pattern_resolver._get_file_and_import_path(request.path)
        self.assertTrue('tests/unit/mocks/apigateway/resolver/pattern_handlers/user/_user_id/item/_item_id_controller.py' in file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.pattern_handlers.user._user_id.item._item_id_controller', import_path)

    # Directory-style coverage using default glob (**/*.py) in PatternModeResolver
    def test_directory_like_get_endpoint_module(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        request = Request(self.basic_request)
        response = Response()
        endpoint_module = resolver.get_endpoint_module(request)
        self.assertTrue(hasattr(endpoint_module, 'post'))
        endpoint_returns = endpoint_module.post(request, response)
        expected = {
            'hasErrors': False,
            'response': {
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': '*'
                },
                'statusCode': 200,
                'isBase64Encoded': False,
                'body': {
                    'directory_basic': True
                }
            }
        }
        self.assertEqual(str(expected), str(endpoint_returns))

    def test_directory_like_basic_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        request = Request(self.basic_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/basic.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.basic', import_path)

    def test_directory_like_nested_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        request = Request(self.nested_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/nested_1/nested_2/basic.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.nested_1.nested_2.basic', import_path)

    def test_directory_like_default_init_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        request = Request(self.init_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/home/__init__.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.home.__init__', import_path)

    def test_directory_like_base_path_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        base_path_request = mock_request.get_basic()
        base_path_request['path'] = self.base_path
        request = Request(base_path_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/__init__.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.__init__', import_path)

    def test_directory_like_base_path_raises_without_init_file(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory_no_root_init)
        base_path_request = mock_request.get_basic()
        base_path_request['path'] = self.base_path
        request = Request(base_path_request)
        with self.assertRaises(ApiException) as resolver_error:
            resolver._get_file_and_import_path(request.path)
        self.assertEqual(resolver_error.exception.code, 404)
        self.assertEqual(resolver_error.exception.message, 'route not found')

    def test_directory_like_dynamic_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        request = Request(self.dynamic_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/dynamic/_id_.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.dynamic._id_', import_path)

    def test_directory_like_triple_dynamic_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        request = Request(self.triple_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/triple/_coordinates.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.triple._coordinates', import_path)

    def test_directory_like_single_nested_dynamic_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        dynamic_nested_request = mock_request.get_dynamic_nested_request_get('user/1')
        request = Request(dynamic_nested_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/user/_user_id/__init__.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.user._user_id.__init__', import_path)

    def test_directory_like_double_nested_dynamic_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        dynamic_nested_request = mock_request.get_dynamic_nested_request_get('user/1/item')
        request = Request(dynamic_nested_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/user/_user_id/item/__init__.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.user._user_id.item.__init__', import_path)

    def test_directory_like_triple_nested_dynamic_get_file_and_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        dynamic_nested_request = mock_request.get_dynamic_nested_request_get('user/1/item/a')
        request = Request(dynamic_nested_request)
        file_path, import_path = resolver._get_file_and_import_path(request.path)
        self.assertIn('tests/unit/mocks/apigateway/resolver/directory_handlers/user/_user_id/item/_item_id.py', file_path)
        self.assertEqual('tests.unit.mocks.apigateway.resolver.directory_handlers.user._user_id.item._item_id', import_path)

    def test_directory_like_repeated_request_resets_import_path(self):
        resolver = PatternModeResolver(base_path=self.base_path, handlers=self.handler_directory)
        request = Request(self.init_request)
        first_file_path, first_import_path = resolver._get_file_and_import_path(request.path)
        second_file_path, second_import_path = resolver._get_file_and_import_path(request.path)
        self.assertEqual(first_file_path, second_file_path)
        self.assertEqual(first_import_path, second_import_path)
