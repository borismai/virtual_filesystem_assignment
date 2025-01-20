from node import Node


class VirtualFileSystem:
    def __init__(self):
        self.main_node = Node(parent=None)

    def add_node(self, path: str, is_dir: bool) -> Node:
        dir_name = self.dirname(path)
        base_name = self.basename(path)
        parent_node = self.get_node_by_path(dir_name)
        node = Node(name=base_name, parent=parent_node, is_dir=is_dir)
        parent_node.add_child(node)
        return node

    def get_node_by_path(self, path: str) -> Node:
        path = path.rstrip('/')
        node_names = path.split('/')
        nodes_list_tmp = [self.main_node]
        node = None
        for node_name in node_names:
            for node in nodes_list_tmp:
                if node.name == node_name:
                    break
            else:
                raise ValueError(f'Not found child node {node_name}')
            nodes_list_tmp = node.get_children() if node.is_dir else None
        if not node:
            raise ValueError(f'Not found child node at all')
        return node

    @classmethod
    def dirname(cls, path: str):
        if not len(path) or path == '/':
            return '/'
        if path[0] != '/':
            path = f"/{path}"
        path = path.rstrip('/')
        parent_names = path.split('/')
        parent_names.pop()
        result = '/'.join(parent_names)
        if not result:
            result = '/'
        return result

    @classmethod
    def basename(cls, path):
        if path in ('', ):
            return path
        path = path.rstrip('/')
        dir_name = cls.dirname(path)
        return path[len(dir_name):].lstrip('/')

    @classmethod
    def normalize_path(cls, path: str):
        dirname = cls.dirname(path)
        if dirname != '/':
            dirname += '/'
        return dirname + cls.basename(path)
