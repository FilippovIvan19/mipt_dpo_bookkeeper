import os

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from tests.test_utils import DB_NAME

import pytest
from dataclasses import dataclass


@pytest.fixture
def custom_class():
    @dataclass
    class Custom:
        pk: int = 0

    return Custom


@pytest.fixture
def repo(custom_class):
    return MemoryRepository[custom_class]()


@pytest.fixture
def sqlite_repo(custom_class):
    return SQLiteRepository[custom_class](DB_NAME, custom_class)


@pytest.fixture(scope='class', autouse=True)
def remove_db_file():
    yield
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)


@pytest.mark.parametrize(
    'rep',
    ['repo', 'sqlite_repo']
)
def test_crud(rep, custom_class, request):
    repo = request.getfixturevalue(rep)
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None


@pytest.mark.parametrize(
    'rep',
    ['repo', 'sqlite_repo']
)
def test_cannot_add_with_pk(rep, custom_class, request):
    repo = request.getfixturevalue(rep)
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


@pytest.mark.parametrize(
    'rep',
    ['repo', 'sqlite_repo']
)
def test_cannot_add_without_pk(rep, request):
    repo = request.getfixturevalue(rep)
    with pytest.raises(ValueError):
        repo.add(0)


@pytest.mark.parametrize(
    'rep',
    ['repo', 'sqlite_repo']
)
def test_cannot_delete_unexistent(rep, request):
    repo = request.getfixturevalue(rep)
    with pytest.raises(KeyError):
        repo.delete(1)


@pytest.mark.parametrize(
    'rep',
    ['repo', 'sqlite_repo']
)
def test_cannot_update_without_pk(rep, custom_class, request):
    repo = request.getfixturevalue(rep)
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)


@pytest.mark.parametrize(
    'rep',
    ['repo', 'sqlite_repo']
)
def test_get_all(rep, custom_class, request):
    repo = request.getfixturevalue(rep)
    objects = [custom_class() for _ in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects


def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.name = str(i)
        o.test = 'test'
        repo.add(o)
        objects.append(o)
    assert repo.get_all({'name': '0'}) == [objects[0]]
    assert repo.get_all({'test': 'test'}) == objects
