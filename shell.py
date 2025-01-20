import fnmatch
import re
from typing import List

from node import Node
from virtual_file_system_advanced import VirtualFileSystem


class Shell:
    def __init__(self, filesystem: VirtualFileSystem, debug: bool = False):
        self.__filesystem = filesystem
        self.__cwd = '/'
        self.__is_debug = debug

        self._menu = 'help – Prints this menu\n' \
                     'md [directory name] – Creates a directory\n' \
                     'cd [directory name] – Changes the current directory\n' \
                     'cd .. – Changes the current directory to parent directory\n' \
                     'mf [file name] [text] – Creates a file and writing text into it\n' \
                     'ls <dir> – Displays list of files and subdirectories in directory\n' \
                     'ls -R <dir> – Recursive. Displays files in specified directory and all subdirectories\n' \
                     'find [directory name] -iname pattern - find files below [directory name] matching a wildcard expression\n' \
                     'grep [file name] [pattern] - search for matching wildcard expression in [file name], output all lines matching pattern.\n' \
                     'cat [file name] - prints the content of [file name].\n' \
                     'pwd - print current working directory.\n' \
                     'exit – Quits the program\n'

    def shell(self):
        while True:
            command = input(f'{self.get_cwd()} $ ')
            result = self.do_command(command)
            print(result)

    def do_command(self, command: str) -> str:
        try:
            args = self.get_args(command)
            if args[0] == 'cat':
                result = self.command_cat(args)
            elif args[0] == 'cd':
                result = self.command_cd(args)
            elif args[0] == 'exit':
                result = None
                self.command_exit(args)
            elif args[0] == 'find':
                result = self.command_find(args)
            elif args[0] == 'grep':
                result = self.command_grep(args)
            elif command.startswith('help'):
                result = self.command_help()
            elif args[0] == 'ls':
                result = self.command_ls(args)
            elif args[0] == 'md':
                result = self.command_md(args)
            elif command.startswith('mf'):
                result = self.command_mf(command)
            elif args[0] == 'pwd':
                result = self.command_pwd(args)
            else:
                raise ValueError(f'Unknown command, use command help')
            return result
        except Exception as e:
            return str(e)

    def command_cat(self, args: List[str]) -> str:
        if len(args) != 2:
            raise ValueError('Invalid arguments')
        filepath_arg = args[1]
        abs_path = self.get_arg_absolute_path(filepath_arg)
        node = self.__filesystem.get_node_by_path(abs_path)
        return node.content

    def command_cd(self, args: List[str]) -> str:
        if len(args) != 2:
            raise ValueError('Invalid arguments')
        dir_arg = args[1]
        if dir_arg == '..':
            abs_path = self.__filesystem.dirname(self.get_cwd())
        else:
            abs_path = self.get_arg_absolute_path(dir_arg)
        self.change_working_directory(abs_path)
        return ''

    def command_help(self):
        return self._menu

    def command_ls(self, args: List[str]) -> str:
        def _recursion(_lines: List[str], _node: Node, is_rec: bool) -> None:
            if _node.is_dir:
                _lines.append(f'{_node.name} START:')
                for child_node in _node.get_children():
                    _lines.append(child_node.name)
                _lines.append('END')

                if is_rec:
                    for child_node in _node.get_children():
                        _recursion(_lines, child_node, is_rec)

        if '-R' in args:
            is_recursive = True
            args.remove('-R')
        else:
            is_recursive = False

        dir_arg = args[1] if len(args) > 1 else self.get_cwd()
        abs_path = self.get_arg_absolute_path(dir_arg)
        node = self.__filesystem.get_node_by_path(abs_path)

        if is_recursive:
            lines = []
            _recursion(lines, node, is_recursive)

            return '\n'.join(lines)
        else:
            return '\n'.join([n.name for n in node.get_children()])

    def command_md(self, args: List[str]) -> str:
        if len(args) < 2:
            raise ValueError('No dir name')

        dir_arg = args[1]
        if dir_arg == '/':
            raise ValueError('Can not create root')

        abs_path = self.get_arg_absolute_path(dir_arg)

        found_node = None
        try:
            found_node = self.__filesystem.get_node_by_path(abs_path)
        except Exception as e:
            pass
        if found_node:
            raise ValueError(f'Path exists {abs_path}')

        dir_names = abs_path.split('/')
        dir_names.pop(0)

        path_current = ''
        for dir_name in dir_names:
            path_current += f'/{dir_name}'
            try:
                node = self.__filesystem.get_node_by_path(path_current)
            except ValueError as exception:
                node_parent = self.__filesystem.get_node_by_path(self.__filesystem.dirname(path_current))
                node_child = Node(parent=node_parent, is_dir=True, name=dir_name)
                node_parent.add_child(node_child)
                self.__debug(f'adding dir {path_current}')
        return ''

    def command_mf(self, command: str):
        match = re.match(r'mf\s+(\S+)\s+(.+)$', command)
        if match:
            file_arg = match[1]
            content_arg = match[2]
            abs_path = self.get_arg_absolute_path(file_arg)
            dir_name = self.__filesystem.dirname(abs_path)
            file_name = self.__filesystem.basename(abs_path)
            Node.check_name(file_name)
            parent_node = self.__filesystem.get_node_by_path(dir_name)
            node = Node(parent=parent_node, name=file_name, is_dir=False)
            node.set_content(content_arg)
            parent_node.add_child(node)
        else:
            raise ValueError('Bad mf command format')

    def command_pwd(self, args: List):
        arg = args[1] if len(args) > 1 else self.get_cwd()
        abs_path = self.get_arg_absolute_path(arg)
        return abs_path

    def get_args(self, command: str) -> List:
        return [x for x in command.split(' ') if len(x)]

    def get_arg_absolute_path(self, path: str) -> str:
        if path.startswith('/'):
            return path
        cwd = self.get_cwd()
        if cwd != '/':
            cwd += '/'
        return cwd + path

    def get_cwd(self):
        return self.__cwd

    def change_working_directory(self, abs_path: str):
        abs_path = self.__filesystem.normalize_path(abs_path)
        node = self.__filesystem.get_node_by_path(abs_path)
        if node.is_dir:
            self.__cwd = abs_path
        else:
            raise ValueError('Final node is not a directory')

    def __debug(self, line):
        if self.__is_debug:
            print(f"{line}\n")

    def command_exit(self, args):
        print('Bye.')
        exit(0)

    def command_grep(self, args: List) -> str:

        def _match(_pattern, _line) -> bool:
            return fnmatch.fnmatch(_line, _pattern)

        if len(args) < 3:
            raise ValueError('Invalid grep command format')

        file_arg = args[1]
        pattern_arg = args[2]

        abs_path = self.get_arg_absolute_path(file_arg)

        found_node = self.__filesystem.get_node_by_path(abs_path)

        return '\n'.join([line for line in found_node.get_content().split('\n') if _match(pattern_arg, line)])

    def command_find(self, args: List) -> str:
        def _rec(_lines: List, _abs_path: str, _pat: str, _node: Node):
            for child in _node.get_children():
                if fnmatch.fnmatch(child.name, _pat):
                    _lines.append(_abs_path + '/' + child.name if _abs_path != '/' else _abs_path + child.name)
                if child.is_dir:
                    next_abs_dir = _abs_path + '/' + child.name if _abs_path != '/' else _abs_path + child.name
                    _rec(_lines, next_abs_dir, _pat, child)

        if len(args) < 4 or args[2] != '-iname':
            raise ValueError('Invalid grep command format')

        dir_arg = args[1]
        abs_path = self.get_arg_absolute_path(dir_arg)
        pattern = args[3]

        node = self.__filesystem.get_node_by_path(abs_path)

        lines = []
        _rec(lines, abs_path, pattern, node)

        return '\n'.join(lines)








