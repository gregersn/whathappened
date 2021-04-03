import pytest

from app.character.schema import get_sub


def test_get_sub():
    main = {
        'a': [1, 2, 3],
        'b': {
            'c': {
                'a': 1,
                'b': 2
            }
        }
    }

    sub = get_sub(main, ['b', 'c'])
    assert sub == main['b']['c']
