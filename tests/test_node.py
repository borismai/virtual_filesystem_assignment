import pytest
from node import Node


def test_check_name():
    Node.check_name('asdasd')
    with pytest.raises(ValueError) as exception:
        Node.check_name(' asdasd')
    assert 'Illegal node name " asdasd"' in str(exception)

    with pytest.raises(ValueError) as exception:
        Node.check_name('')
    assert 'Illegal node name ""' in str(exception)
