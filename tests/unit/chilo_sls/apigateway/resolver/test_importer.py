import os
import unittest

from chilo_sls.apigateway.resolver.importer import ResolverImporter
from chilo_sls.apigateway.exception import ApiException


class ResolverImporterTest(unittest.TestCase):
    maxDiff = None
    handler_path = 'tests/unit/mocks/apigateway/importer/directory_handlers'
    handler_bad_multi_dynamic = 'tests/unit/mocks/apigateway/importer/bad_handlers/multi-dynamic'
    handler_bad_same_name = 'tests/unit/mocks/apigateway/importer/bad_handlers/same-name'
    handler_should_pass = 'tests/unit/mocks/apigateway/importer/bad_handlers/should-pass'
    expected_directory_file_tree = {
        '__init__.py': '*',
        '__dynamic_files': {'_dynamic'},
        'basic.py': '*',
        '_dynamic': {
            '__init__.py': '*',
            '__dynamic_files': set()
        },
        'nested_1': {
            '__init__.py': '*',
            '__dynamic_files': set(),
            'nested_2': {
                '__init__.py': '*',
                '__dynamic_files': {'_id.py'},
                '_id.py': '*',
                'basic.py': '*'
            }
        }
    }
    expected_passing_shared_name_diff_levels = {
        '__init__.py': '*',
        '__dynamic_files': set(),
        'good_file.py': '*',
        'good_directory': {
            '__init__.py': '*',
            '__dynamic_files': set(),
            'good_file.py': '*'
        }
    }

    def test_clean_path(self):
        importer = ResolverImporter(handlers=self.handler_path, mode='directory')
        self.assertEqual(importer.clean_path('/dirty/path/'), 'dirty/path')

    def test_clean_handlers(self):
        importer = ResolverImporter(handlers=self.handler_path, mode='directory')
        self.assertEqual(importer.handlers, self.handler_path)

    def test_dirty_handlers(self):
        dirty_path = '/tests/unit/mocks/apigateway/importer/directory_handlers/'
        importer = ResolverImporter(handlers=dirty_path, mode='directory')
        self.assertEqual(importer.handlers, self.handler_path)

    def test_handlers_file_tree_directory_mode(self):
        importer = ResolverImporter(handlers=self.handler_path, mode='directory')
        self.assertDictEqual(self.expected_directory_file_tree, importer.get_handlers_file_tree())

    def test_handlers_file_throw_exception_on_two_dynamic_files(self):
        importer = ResolverImporter(handlers=self.handler_bad_multi_dynamic, mode='directory')
        try:
            print(importer.get_handlers_file_tree())
        except ApiException as importer_error:
            self.assertTrue(isinstance(importer_error, ApiException))
            self.assertTrue('Cannot have two dynamic files in the same directory.' in importer_error.message)

    def test_handlers_file_throw_exception_on_directory_and_file_share_name(self):
        importer = ResolverImporter(handlers=self.handler_bad_same_name, mode='directory')
        try:
            print(importer.get_handlers_file_tree())
            self.assertTrue(False)
        except ApiException as importer_error:
            self.assertTrue(isinstance(importer_error, ApiException))
            self.assertTrue('Cannot have file and directory share same name.' in importer_error.message)

    def test_handlers_file_should_allow_directory_and_file_share_name_on_different_levels(self):
        importer = ResolverImporter(handlers=self.handler_should_pass, mode='directory')
        self.assertDictEqual(self.expected_passing_shared_name_diff_levels, importer.get_handlers_file_tree())

    def test_import_module_from_file(self):
        importer = ResolverImporter(handlers=self.handler_path, mode='directory')
        file_path = f'{self.handler_path}/basic.py'
        import_path = 'tests.unit.mocks.apigateway.importer.directory_handlers.basic'
        handler_module = importer.import_module_from_file(file_path, import_path)
        self.assertTrue(hasattr(handler_module, 'post'))
