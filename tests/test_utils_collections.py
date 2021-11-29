from whathappened.utils.collections import ChainedSheet


def test_sheet():
    data = {}

    base = {
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
        }
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

    sheet['stats']['str'] = 5
    assert 'stats' in data
    assert data['stats']['str'] == 5
    assert base['stats']['str'] == 4

    assert sheet.changes() == result
