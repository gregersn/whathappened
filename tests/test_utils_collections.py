from typing import Any, Dict, MutableSequence
from whathappened.utils.collections import ChainedSheet, ChangedList


def test_sheet():
    data: Dict[str, Any] = {}

    base: Dict[str, Any] = {
        'name': 'Ace',
        'stats': {
            'str': 4,
            'dex': 2
        },
        'equipment': ['shovel', 'rope']
    }

    result = {
        'name': 'Base',
        'stats': {
            'str': 5
        },
        'equipment': ['shovel', 'rope', 'torch']
    }

    result2 = {
        'name': 'Base',
        'stats': {
            'str': 5
        },
        'equipment': ['rope', 'torch']
    }

    sheet = ChainedSheet(data, base)

    assert sheet['name'] == 'Ace'
    sheet['name'] = 'Base'
    assert sheet['name'] == 'Base'
    assert data['name'] == 'Base'
    assert base['name'] == 'Ace'

    assert 'stats' not in data
    assert base['stats']['str'] == 4
    assert sheet['stats']['str'] == 4

    assert sheet['stats'] is not None
    assert sheet['stats']['str'] is not None

    sheet['stats']['str'] = 5

    assert 'stats' in data
    assert data['stats']['str'] == 5
    assert base['stats']['str'] == 4

    assert 'equipment' not in data
    assert sheet['equipment'] == ['shovel', 'rope']
    sheet['equipment'].append('torch')
    assert 'equipment' in data

    assert sheet.changes() == result
    assert isinstance(sheet['equipment'], MutableSequence)
    sheet['equipment'].remove('shovel')
    assert sheet.changes() == result2


def test_sheet_system():
    data: Dict[str, Any] = {"system": "foo"}
    base_data: Dict[str, Any] = {"system": "foo",
                                 "name": "moo", "attributes": {"a": 1, "b": 2}}

    sheet = ChainedSheet(data, base_data)

    assert sheet['name'] == "moo"
    assert sheet['system'] == "foo"

    res = sheet.changes()

    assert res == data


def test_sheet_overlap():
    data: Dict[str, Any] = {"a": "b", "c": {"d": "e"}}
    base_data: Dict[str, Any] = {"c": {"f": "g"}}

    sheet = ChainedSheet(data, base_data)

    assert sheet['c']['d'] == 'e'
    assert sheet['c']['f'] == 'g'


def test_list_copy():
    data: Dict[str, Any] = {
        "my": {
            "goal": "To lose"
        }
    }
    base_data: Dict[str, Any] = {
        "my": {
            "inventory": [
                "Consortium uniform",
                "Communicator",
                "Pistol"
            ],
            "goal": "Meet new aliens and have fun with them!"
        }
    }

    sheet = ChainedSheet(data, base_data)

    sheet['my']['goal'] = 'To win!'

    assert 'inventory' not in sheet.changes()['my']


def test_changed_list():
    l = ChangedList(['a', 'b', 'c'])

    assert l.changed == False

    l.append('d')
    assert l.changed == True
