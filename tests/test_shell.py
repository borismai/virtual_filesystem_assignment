import pytest

from shell import Shell
from virtual_file_system_advanced import VirtualFileSystem


def test_command_cd():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)
    vfs.add_node('/d1/d2', is_dir=True)
    vfs.add_node('/d1/d3', is_dir=True)
    vfs.add_node('/d1/f1', is_dir=False)

    shell = Shell(vfs)

    assert shell.get_cwd() == '/'

    shell.do_command('cd d1')
    assert shell.get_cwd() == '/d1'

    shell.do_command('cd /d1/d3')
    assert shell.get_cwd() == '/d1/d3'

    result = shell.do_command('cd /d1/f1')
    assert 'Final node is not a dir' in result

    result = shell.do_command('cd ')
    assert 'Invalid arg' in result

    shell.do_command('cd /d1/d3')
    shell.do_command('cd ..')
    assert shell.get_cwd() == '/d1'
    shell.do_command('cd ..')
    assert shell.get_cwd() == '/'


def test_commands_mf_and_cat():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)

    shell = Shell(vfs)

    shell.do_command('mf /d1/some.file  123 123 12 132')
    result = shell.do_command('cat /d1/some.file')
    assert result == '123 123 12 132'
    # file already exists
    result = shell.do_command('mf /d1/some.file  123 123 12 132')
    assert 'Child with name "some.file" already exists' in result

    # non-absolute path
    shell.do_command('cd /d1/')
    result = shell.do_command('cat some.file')
    assert result == '123 123 12 132'

    result = shell.do_command('mf /NOT_EXISTS/some.file  123 123 12 132')
    assert 'Not found child node NOT_EXISTS' in result


def test_command_ls():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)
    vfs.add_node('/d1/d2', is_dir=True)
    vfs.add_node('/d1/d3', is_dir=True)
    vfs.add_node('/d1/f1', is_dir=False)

    shell = Shell(vfs)

    assert shell.do_command('ls') == 'd1'
    assert shell.do_command('ls /d1') == 'd2\nd3\nf1'
    assert shell.do_command('ls d1') == 'd2\nd3\nf1'
    assert shell.do_command('ls d1/d2') == ''

    assert 'File has no children' in shell.do_command('ls /d1/f1')


def test_command_ls_r():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)
    vfs.add_node('/d1/d2', is_dir=True)
    vfs.add_node('/d1/d3', is_dir=True)
    vfs.add_node('/d1/f1', is_dir=False)

    shell = Shell(vfs)

    assert shell.do_command('ls -R /') == ' START:\nd1\nEND\nd1 START:\nd2\nd3\nf1\nEND\nd2 START:\nEND\nd3 START:\nEND'
    assert shell.do_command('ls -R /d1') == 'd1 START:\nd2\nd3\nf1\nEND\nd2 START:\nEND\nd3 START:\nEND'
    assert shell.do_command('ls -R d1') == 'd1 START:\nd2\nd3\nf1\nEND\nd2 START:\nEND\nd3 START:\nEND'

    shell.do_command('cd /d1')
    assert shell.do_command('ls -R') == 'd1 START:\nd2\nd3\nf1\nEND\nd2 START:\nEND\nd3 START:\nEND'
    assert shell.do_command('ls -R d2') == 'd2 START:\nEND'


def test_command_pwd():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)
    vfs.add_node('/d1/d2', is_dir=True)
    vfs.add_node('/d1/d3', is_dir=True)

    shell = Shell(vfs)

    assert shell.do_command('pwd') == '/'
    shell.do_command('cd /d1')
    assert shell.do_command('pwd') == '/d1'
    assert shell.do_command('pwd d3') == '/d1/d3'


def test_command_md():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)

    shell = Shell(vfs, debug=True)

    shell.do_command('md /d1')
    assert shell.do_command('ls /') == 'd1'

    shell.do_command('md /d2')
    assert shell.do_command('ls /') == 'd1\nd2'
    assert 'exists' in shell.do_command('md /d2')

    shell.do_command('md /rec1/rec2/rec3')
    assert shell.do_command('ls /') == 'd1\nd2\nrec1'
    assert shell.do_command('ls /rec1') == 'rec2'
    assert shell.do_command('ls /rec1/rec2') == 'rec3'

    shell.do_command('md /rec1/rec2/rec3/rec4')
    assert shell.do_command('ls /rec1/rec2/rec3') == 'rec4'


def test_command_grep():
    vfs = VirtualFileSystem()
    shell = Shell(vfs, debug=True)

    shell.do_command('mf f1 123 123')
    assert '123 123' in shell.do_command('grep f1 123*')
    assert '123 123' in shell.do_command('grep f1 123*123')
    assert '' == shell.do_command('grep f1 NOT_MATCHING')


def test_command_find():
    vfs = VirtualFileSystem()
    vfs.add_node('/d1', is_dir=True)
    vfs.add_node('/d1/d2', is_dir=True)
    vfs.add_node('/d1/d3', is_dir=True)
    vfs.add_node('/d1/f1', is_dir=False)
    shell = Shell(vfs, debug=True)

    shell.do_command('find / -iname f1')
    assert '/d1/f1' in shell.do_command('find / -iname f1')
    assert 'd1/f1' in shell.do_command('find / -iname f1')
    assert '/d1/f1' in shell.do_command('find / -iname f*')

    result = shell.do_command('find / -iname *')
    assert '/d1' in result
    assert '/d1/d2' in result
    assert '/d1/d3' in result
    assert '/d1/f1' in result
