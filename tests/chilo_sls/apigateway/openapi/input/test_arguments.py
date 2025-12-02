import unittest
from unittest.mock import patch

from chilo_sls.apigateway.openapi.input.arguments import InputArguments


class InputArgumentsTest(unittest.TestCase):

    @patch('sys.argv', [
        'InputArguments',
        'generate-openapi',
        '--base=chilo_sls/example',
        '--handlers=tests/mocks/apigateway/openapi/**/*.py',
        '--output=tests/outputs/arguments',
        '--format=json,yml',
        '--delete'
    ])
    def test_full_class(self):
        input_args = InputArguments()
        self.assertEqual('chilo_sls/example', input_args.base)
        self.assertEqual('tests/mocks/apigateway/openapi/**/*.py', input_args.handlers)
        self.assertEqual('tests/outputs/arguments', input_args.output)
        self.assertListEqual(['json', 'yml'], input_args.formats)
        self.assertTrue(input_args.delete)
