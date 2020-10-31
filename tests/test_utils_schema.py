import os
import pytest

from app.utils.schema import migrate, up_or_down, find_migration

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def test_up_or_down():
    assert up_or_down("1.0.0", "1.0.0") == 0
    assert up_or_down("1.0.0", "1.0.1") == 1
    assert up_or_down("1.0.1", "1.0.0") == -1


def test_migrate_same():
    data = {"meta": {
        "Version": "1.0.0"
    }}

    migrated = migrate(data, "1.0.0")

    assert migrated == data


def v1_0_0_to_v1_0_1(data):
    new_schema = data.copy()
    data['meta']['Version'] = "1.0.1"
    return new_schema


def v1_0_1_to_v1_0_0(data):
    new_schema = data.copy()
    data['meta']['Version'] = "1.0.0"
    return new_schema


migrations = [
    {
        'from': '0.9',
        'to': '1.0.0'
    },
    {
        'from': "1.0.0",
        'to': "1.0.1",
        'up': v1_0_0_to_v1_0_1,
        'down': v1_0_1_to_v1_0_0
    },
    {
        'from': '1.0.1',
        'to': '1.0.2'
    }
]


def test_migrate_up():
    data = {"meta": {
        "Version": "1.0.0"
    }}

    migrated = migrate(data, "1.0.1", migrations=migrations)

    assert migrated['meta']['Version'] == "1.0.1"


def test_migrate_down():
    data = {"meta": {
        "Version": "1.0.1"
    }}

    migrated = migrate(data, "1.0.0", migrations=migrations)

    assert migrated['meta']['Version'] == "1.0.0"
