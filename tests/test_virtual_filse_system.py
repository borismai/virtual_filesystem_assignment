import pytest

from virtual_file_system_advanced import VirtualFileSystem


def test_get_node_by_path():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)
    vfs.add_node('/d1/d2', is_dir=True)
    assert vfs.get_node_by_path('/d1').name == 'd1'
    assert vfs.get_node_by_path('/d1/d2/').name == 'd2'


def test_get_content():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)
    vfs.add_node('/d1/d2', is_dir=True)
    vfs.add_node('/d1/d2/f1.txt', is_dir=False)
    node_file = vfs.get_node_by_path('/d1/d2/f1.txt')
    node_file.set_content('123')
    assert vfs.get_node_by_path('/d1/d2/f1.txt').get_content() == '123'


def test_dirname():
    assert VirtualFileSystem.dirname('') == '/'
    assert VirtualFileSystem.dirname('/') == '/'
    assert VirtualFileSystem.dirname('/asdf') == '/'
    assert VirtualFileSystem.dirname('/asdf/') == '/'
    assert VirtualFileSystem.dirname('/asdf/rw') == '/asdf'
    assert VirtualFileSystem.dirname('/asdf/rw/') == '/asdf'
    assert VirtualFileSystem.dirname('/asdf/rw.txt') == '/asdf'


def test_basename():
    assert VirtualFileSystem.basename('/') == ''
    assert VirtualFileSystem.basename('/asdf') == 'asdf'
    assert VirtualFileSystem.basename('/asdf/') == 'asdf'
    assert VirtualFileSystem.basename('/asdf/rw') == 'rw'
    assert VirtualFileSystem.basename('/asdf/rw/') == 'rw'
    assert VirtualFileSystem.basename('/asdf/rw.txt') == 'rw.txt'


def test_normalize_path():
    assert VirtualFileSystem.normalize_path('/') == '/'
    assert VirtualFileSystem.normalize_path('/asdf') == '/asdf'
    assert VirtualFileSystem.normalize_path('/asdf/') == '/asdf'
    assert VirtualFileSystem.normalize_path('/asdf/rw') == '/asdf/rw'
    assert VirtualFileSystem.normalize_path('/asdf/rw/') == '/asdf/rw'
    assert VirtualFileSystem.normalize_path('/asdf/rw.txt') == '/asdf/rw.txt'
