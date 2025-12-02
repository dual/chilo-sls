import json
import unittest
from unittest.mock import patch

from chilo_sls.apigateway.router import Router

from tests.mocks.apigateway import mock_middleware, mock_request


class RouterPatternTest(unittest.TestCase):
    maxDiff = None
    base_path = 'unit-test/v1'
    handler_pattern = 'tests/mocks/apigateway/router/pattern_handlers/**/*_controller.py'
    schema_path = 'tests/mocks/apigateway/openapi.yml'
    base_path_schema_path = 'tests/mocks/apigateway/base_path_openapi.yml'
    basic_event = mock_request.get_basic_post()
    raise_exception_event = mock_request.get_raised_exception_post()
    mock_request = mock_request
    unhandled_exception_event = mock_request.get_unhandled_exception_post()
    expected_open_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*'
    }
    startup_hooks = [mock_middleware.mock_on_startup]
    shutdown_hooks = [mock_middleware.mock_on_shutdown]

    def test_basic_pattern_routing_works(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(self.basic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertFalse(result['isBase64Encoded'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual(self.expected_open_headers, result['headers'])
        self.assertDictEqual({"router_pattern_basic": {"body_key": "body_value"}}, json_dict_response)

    def test_basic_directory_routing_works_with_ending_path_parameters(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'x-api-key': 'some-key'},
            path='unit-test/v1/triple/1/2/3',
            proxy='triple',
            method='post'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertFalse(result['isBase64Encoded'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual(self.expected_open_headers, result['headers'])
        self.assertDictEqual({'pattern_triple_coordinates': {'proxy': 'triple', 'x': '1', 'y': '2', 'z': '3'}}, json_dict_response)

    def test_basic_pattern_routing_works_with_verbose(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path,
            verbose=True
        )
        result = router.route(self.basic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertFalse(result['isBase64Encoded'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual(self.expected_open_headers, result['headers'])
        self.assertDictEqual({"router_pattern_basic": {"body_key": "body_value"}}, json_dict_response)

    def test_auto_load_works(self):
        try:
            router = Router(
                base_path=self.base_path,
                handlers=self.handler_pattern,
                openapi=self.schema_path
            )
            router.auto_load()
            self.assertTrue(True)
        except Exception as error:
            print(error)
            self.assertTrue(False)

    def test_basic_pattern_routing_works_no_schema_defined(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern
        )
        result = router.route(self.basic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertFalse(result['isBase64Encoded'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual(self.expected_open_headers, result['headers'])
        self.assertDictEqual({"router_pattern_basic": {"body_key": "body_value"}}, json_dict_response)

    def test_basic_pattern_routing_works_with_raised_exception(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(self.raise_exception_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertFalse(result['isBase64Encoded'])
        self.assertEqual(418, result['statusCode'])
        self.assertDictEqual(self.expected_open_headers, result['headers'])
        self.assertDictEqual({"errors": [{"key_path": "crazy_error", "message": "I am a teapot"}]}, json_dict_response)

    def test_basic_pattern_routing_works_with_unhandled_exception(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path,
            output_error=True
        )
        result = router.route(self.unhandled_exception_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertFalse(result['isBase64Encoded'])
        self.assertEqual(500, result['statusCode'])
        self.assertDictEqual(self.expected_open_headers, result['headers'])
        self.assertDictEqual({'errors': [{'key_path': 'unknown', 'message': "name 'UnknownException' is not defined"}]}, json_dict_response)

    def test_basic_pattern_routing_works_and_before_all_function_called(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            before_all=mock_middleware.mock_before_all,
            openapi=self.schema_path
        )
        router.route(self.basic_event, None)
        self.assertTrue(mock_middleware.mock_before_all.has_been_called)

    def test_basic_pattern_routing_works_and_after_all_function_called(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            after_all=mock_middleware.mock_after_all,
            openapi=self.schema_path
        )
        router.route(self.basic_event, None)
        self.assertTrue(mock_middleware.mock_after_all.has_been_called)

    def test_basic_pattern_routing_works_and_when_auth_required_function_called(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            when_auth_required=mock_middleware.mock_when_auth_required,
            openapi=self.schema_path
        )
        router.route(self.basic_event, None)
        self.assertTrue(mock_middleware.mock_when_auth_required.has_been_called)
        mock_middleware.mock_when_auth_required.has_been_called = False

    def test_basic_pattern_routing_works_and_on_error_function_called(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            on_error=mock_middleware.mock_on_error,
            openapi=self.schema_path
        )
        router.route(self.raise_exception_event, None)
        self.assertTrue(mock_middleware.mock_on_error.has_been_called)

    def test_basic_pattern_routing_works_and_bad_on_error_function_caught(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            on_error=mock_middleware.mock_on_error_exception,
            openapi=self.schema_path
        )
        router.route(self.raise_exception_event, None)
        self.assertTrue(mock_middleware.mock_on_error_exception.has_been_called)

    def test_requirements_decorator_works_and_passes_proper_body_request(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json'},
            path='unit-test/v1/nested/reqs',
            proxy='nested/reqs',
            method='post',
            body={
                'name': 'unit-test',
                'email': 'unit@email.com',
                'phone': 1234567890,
                'active': True
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(dynamic_event, None)
        self.assertEqual(200, result['statusCode'])

    def test_requirements_decorator_works_and_fails_improper_body_request(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json'},
            path='unit-test/v1/nested/reqs',
            proxy='nested/reqs',
            method='post',
            body={
                'name': 'unit-test',
                'email': 'unit@email.com',
                'phone': '1234567890',
                'active': True
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(dynamic_event, None)
        self.assertEqual(400, result['statusCode'])
        json_dict_response = json.loads(result['body'])
        self.assertDictEqual({'errors': [{'key_path': 'phone', 'message': "'1234567890' is not of type 'number'"}]}, json_dict_response)

    def test_requirements_decorator_works_and_passes_proper_query_request(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json'},
            path='unit-test/v1/nested/reqs',
            proxy='nested/reqs',
            method='get',
            query={
                'auth_id': 'some-id',
                'email': 'some@email.com',
                'name': 'unit-test'
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(dynamic_event, None)
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual(self.expected_open_headers, result['headers'])

    def test_requirements_decorator_works_and_fails_improper_query_request_missing_required(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json'},
            path='unit-test/v1/nested/reqs',
            proxy='nested/reqs',
            method='get',
            query={
                'email': 'some@email.com',
                'name': 'unit-test'
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern
        )
        result = router.route(dynamic_event, None)
        self.assertEqual(400, result['statusCode'])
        json_dict_response = json.loads(result['body'])
        self.assertDictEqual({'errors': [{'key_path': 'query_params', 'message': 'Please provide auth_id in query_params'}]}, json_dict_response)

    def test_requirements_decorator_works_and_passes_proper_headers(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json', 'correlation-id': 'abc-123'},
            path='unit-test/v1/nested/reqs',
            proxy='nested/reqs',
            method='delete'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern
        )
        result = router.route(dynamic_event, None)
        self.assertEqual(200, result['statusCode'])

    def test_requirements_decorator_works_and_fails_improper_headers_missing_required(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'correlation-id': 'abc-123'},
            path='unit-test/v1/nested/reqs',
            proxy='nested/reqs',
            method='delete'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(400, result['statusCode'])
        self.assertDictEqual({'errors': [{'key_path': 'headers', 'message': 'Please provide content-type in headers'}]}, json_dict_response)

    def test_requirements_decorator_works_and_fails_improper_headers_unknown_header(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'unknown-id': 'abc-123'},
            path='unit-test/v1/nested/reqs',
            proxy='nested/reqs',
            method='delete'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(400, result['statusCode'])
        self.assertDictEqual(
            {
                'errors': [{'key_path': 'headers', 'message': 'Please provide content-type in headers'},
                           {'key_path': 'headers', 'message': 'unknown-id is not an available headers'}]
            }, json_dict_response
        )

    def test_requirements_decorator_works_and_passes_proper_dynamic_route_request(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json'},
            path='unit-test/v1/nested/abc-123',
            proxy='nested/abc-123',
            method='patch',
            body={
                'test_id': 'unit-test',
                'email': 'unit@email.com'
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual(
            {
                'router_nested_pattern_dynamic': {'test_id': 'unit-test', 'email': 'unit@email.com'},
                'path_params': {'proxy': 'nested/abc-123', 'nested_id': 'abc-123'}
            },
            json_dict_response
        )

    def test_pattern_dynamic_route_preserves_hyphenated_param_value(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json'},
            path='unit-test/v1/nested/abc-123',
            proxy='nested/abc-123',
            method='patch',
            body={
                'test_id': 'unit-test',
                'email': 'unit@email.com'
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])

        nested_id = json_dict_response['path_params']['nested_id']
        self.assertEqual('abc-123', nested_id)

    def test_pattern_dynamic_route_does_not_convert_hyphenated_param(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json'},
            path='unit-test/v1/nested/abc-123',
            proxy='nested/abc-123',
            method='patch',
            body={
                'test_id': 'unit-test',
                'email': 'unit@email.com'
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])

        nested_id = json_dict_response['path_params']['nested_id']
        self.assertNotEqual('abc_123', nested_id)

    def test_requirements_decorator_works_and_fails_improper_dynamic_route_request(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json'},
            path='unit-test/v1/nested/abc-123',
            proxy='nested/abc-123',
            method='patch',
            body={
                'email': 'unit@email.com'
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(400, result['statusCode'])
        self.assertDictEqual({'errors': [{'key_path': 'root', 'message': "'test_id' is a required property"}]}, json_dict_response)

    def test_basic_pattern_routing_works_with_openapi_validate_response_body(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'x-api-key': 'some-key'},
            path='unit-test/v1/auto',
            proxy='auto',
            method='patch'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual({'page_number': 1, 'data': {'id': '2'}}, json_dict_response)

    def test_openapi_validate_request_works_and_passes_proper_dynamic_route_request(self):
        body = {
            'test_id': 'abc123',
            'object_key': {
                'key': 'value'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'string_value',
                    'array_number_key': 0
                }
            ]
        }
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json', 'x-api-key': 'some-key'},
            path='unit-test/v1/auto',
            proxy='auto',
            method='post',
            body=body
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path,
            openapi_validate_request=True
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual({'router_pattern_auto': body}, json_dict_response)

    def test_openapi_validate_request_works_and_fails_improper_dynamic_route_request(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'content-type': 'application/json', 'x-api-key': 'some-key'},
            path='unit-test/v1/auto',
            proxy='auto',
            method='post',
            body={
                'object_key': {
                    'key': 'value'
                },
                'array_number': [1, 2, 3],
                'array_objects': [
                    {
                        'array_string_key': 'string_value',
                        'array_number_key': 0
                    }
                ]
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path,
            openapi_validate_request=True
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(400, result['statusCode'])
        self.assertDictEqual({'errors': [{'key_path': 'root', 'message': "'test_id' is a required property"}]}, json_dict_response)

    def test_openapi_validate_request_works_and_passes_proper_dynamic_route_request_with_optional_params(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'x-api-key': 'some-key'},
            path='unit-test/v1/optional-params',
            proxy='optional-params',
            method='get',
            query={
                'group': 'some-group'
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path,
            openapi_validate_request=True
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual({'router_pattern_optional': True}, json_dict_response)

    def test_openapi_validate_request_works_with_base_path_and_optional_params(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'x-api-key': 'some-key'},
            path='unit-test/v1/optional-params',
            proxy='optional-params',
            method='get',
            query={
                'group': 'some-group'
            }
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.base_path_schema_path,
            openapi_validate_request=True
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual({'router_pattern_optional': True}, json_dict_response)

    def test_basic_pattern_routing_works_with_openapi_validate_request_and_when_auth_required_function_called(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'x-api-key': 'some-key'},
            path='unit-test/v1/auto',
            proxy='auto',
            method='get'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            when_auth_required=mock_middleware.mock_when_auth_required,
            openapi=self.schema_path,
            openapi_validate_request=True
        )
        router.route(dynamic_event, None)
        self.assertTrue(mock_middleware.mock_when_auth_required.has_been_called)
        mock_middleware.mock_when_auth_required.has_been_called = False

    def test_warmup_calls_startup_hooks(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            on_startup=self.startup_hooks,
            openapi=self.schema_path
        )
        router.warmup()
        self.assertTrue(mock_middleware.mock_on_startup.has_been_called)
        mock_middleware.mock_on_startup.has_been_called = False

    def test_cooldown_calls_shutdown_hooks(self):
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            on_shutdown=self.shutdown_hooks,
            openapi=self.schema_path
        )
        router.cooldown()
        self.assertTrue(mock_middleware.mock_on_shutdown.has_been_called)
        mock_middleware.mock_on_shutdown.has_been_called = False

    def test_cooldown_auto_registered_and_calls_shutdown_hooks(self):
        registered = {}

        def fake_register(fn):
            registered['fn'] = fn

        called = {'count': 0}

        def hook():
            called['count'] += 1

        with patch('chilo_sls.apigateway.router.atexit.register', side_effect=fake_register):
            Router(
                base_path=self.base_path,
                handlers=self.handler_pattern,
                on_shutdown=[hook],
                openapi=self.schema_path
            )

        self.assertIn('fn', registered)
        registered['fn']()
        self.assertEqual(called['count'], 1)

    def test_basic_pattern_routing_works_with_openapi_validate_request_response_body(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'x-api-key': 'some-key'},
            path='unit-test/v1/auto',
            proxy='auto',
            method='get'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path,
            openapi_validate_request=True,
            openapi_validate_response=True
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(200, result['statusCode'])
        self.assertDictEqual({'page_number': 1, 'data': {'id': '2'}}, json_dict_response)

    def test_basic_pattern_routing_fails_with_openapi_validate_request_response_body(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'x-api-key': 'some-key'},
            path='unit-test/v1/auto',
            proxy='auto',
            method='put'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path,
            openapi_validate_request=True,
            openapi_validate_response=True
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(500, result['statusCode'])
        self.assertDictEqual(
            {
                'errors': [
                    {
                        'key_path': 'root',
                        'message': "'data' is a required property"
                    },
                    {
                        'key_path': 'root',
                        'message': "Additional properties are not allowed ('bad-put' was unexpected)"
                    },
                    {
                        'key_path': 'response',
                        'message': 'There was a problem with the APIs response; does not match defined schema'
                    }
                ]
            },
            json_dict_response
        )

    def test_basic_pattern_routing_fails_with_response_body(self):
        dynamic_event = self.mock_request.get_dynamic_event(
            headers={'x-api-key': 'some-key'},
            path='unit-test/v1/auto',
            proxy='auto',
            method='delete'
        )
        router = Router(
            base_path=self.base_path,
            handlers=self.handler_pattern,
            openapi=self.schema_path,
            openapi_validate_response=True
        )
        result = router.route(dynamic_event, None)
        json_dict_response = json.loads(result['body'])
        self.assertEqual(500, result['statusCode'])
        self.assertDictEqual(
            {
                'errors': [
                    {
                        'key_path': 'root',
                        'message': "'data' is a required property"
                    },
                    {
                        'key_path': 'root',
                        'message': "Additional properties are not allowed ('bad-delete' was unexpected)"
                    },
                    {
                        'key_path': 'response',
                        'message': 'There was a problem with the APIs response; does not match defined schema'
                    }
                ]
            },
            json_dict_response
        )
