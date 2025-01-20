from typing import List
import re

from constants import node_name_pattern


class Node:
    def __init__(self, parent=None, name: str = '', is_dir: bool = True) -> None:
        self.children = []
        if parent:
            self.name = name
            self.is_dir = is_dir
            self.check_name(name)
        else:
            self.name = ''
            self.is_dir = True

        if self.is_dir:
            self.content = None
        else:
            self.content = ''

    @classmethod
    def check_name(cls, name) -> None:
        if not re.match(f"^{node_name_pattern}$", name):
            raise ValueError(f'Illegal node name "{name}"')

    def get_children(self) -> List:
        if self.is_dir:
            return self.children
        raise ValueError('File has no children')

    def get_child(self, name: str):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def add_child(self, node):
        node_old = self.get_child(node.name)
        if node_old:
            raise ValueError(f'Child with name "{node.name}" already exists')
        self.children.append(node)

    def get_content(self):
        if self.is_dir:
            raise ValueError('Dir has no content')
        return self.content

    def set_content(self, content: str):
        if self.is_dir:
            raise ValueError('Dir has no content')
        self.content = content
