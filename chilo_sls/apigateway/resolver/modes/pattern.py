from chilo_sls.apigateway.resolver.modes.base import BaseModeResolver
from chilo_sls.apigateway.exception import ApiException


class PatternModeResolver(BaseModeResolver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        handlers = kwargs['handlers']
        # default to recursive glob when given a directory
        if '*' not in handlers and '.py' not in handlers:
            handlers = self.importer.clean_path(handlers) + f'{self.importer.file_separator}**{self.importer.file_separator}*.py'
        self.__handler_pattern = handlers

    def _get_file_and_import_path(self, request_path):
        # ensure previous lookups don't leave behind path/dynamic state
        self.reset()
        split_path = self.get_request_path_as_list(request_path)
        route_path = self.__get_relative_path(split_path)
        file_path = self.__handler_pattern.split(f'{self.importer.file_separator}*')[0] + self.importer.file_separator + route_path
        import_path = self.get_import_path(file_path)
        return file_path, import_path

    def __get_relative_path(self, split_path):
        file_tree = self.importer.get_handlers_file_tree()
        file_pattern = self.__get_file_pattern()
        self.__get_import_path_file_tree(split_path, 0, file_tree, file_pattern)
        return f'{self.importer.file_separator}'.join(self.import_path)

    def __get_file_pattern(self):
        split_pattern = self.__handler_pattern.split(self.importer.file_separator)
        file_pattern = split_pattern[-1]
        return file_pattern

    def __get_import_path_file_tree(self, split_path, split_index, file_tree, file_pattern):
        if split_index >= len(split_path):
            return

        import_part = self.__select_import_part(split_path, split_index, file_tree, file_pattern)
        if import_part is None:
            raise ApiException(code=404, message='route not found')

        self.append_import_path(import_part)
        file_leaf = self.determine_which_file_leaf(file_tree, import_part)
        path_state = self.__build_path_state(split_index, split_path, import_part)
        if self.__append_index_if_leaf(import_part, file_leaf, file_pattern, path_state):
            return
        if import_part == '__init__.py':
            return
        self.__get_import_path_file_tree(split_path, split_index+1, file_leaf, file_pattern)

    def __select_import_part(self, split_path, split_index, file_tree, file_pattern):
        route_part = split_path[split_index].replace('-', '_')
        if route_part == '':
            return '__init__.py' if '__init__.py' in file_tree else None

        possible_directory = f'{route_part}'
        possible_file = file_pattern.replace('*', route_part)
        if possible_directory in file_tree:
            return possible_directory
        if possible_file in file_tree:
            return possible_file
        if file_tree.get('__dynamic_files') and file_tree['__dynamic_files']:
            import_part = list(file_tree['__dynamic_files'])[0]
            self.has_dynamic_route = True
            self.dynamic_parts[split_index] = split_path[split_index]
            return import_part
        return None

    def __build_path_state(self, split_index, split_path, import_part):
        return {
            'is_last': split_index + 1 == len(split_path),
            'is_directory': '.py' not in import_part
        }

    def __append_index_if_leaf(self, import_part, file_leaf, file_pattern, path_state):
        index_file = file_pattern.replace('*', import_part)
        if path_state['is_directory'] and path_state['is_last']:
            if index_file in file_leaf:
                self.append_import_path(index_file)
                return True
            if isinstance(file_leaf, dict) and '__init__.py' in file_leaf:
                self.append_import_path('__init__.py')
                return True
        return False
