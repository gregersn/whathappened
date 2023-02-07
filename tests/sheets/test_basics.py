from pathlib import Path
from whathappened.sheets import new_sheet

test_schema_file = Path(__file__).parent / "test_schema.yml"


def test_new_sheet():

    sheet = new_sheet(test_schema_file)
    assert sheet['system'] == 'testsheet'
    assert sheet['meta']['gamename'] == 'Test sheet'
    assert sheet['character_sheet']['name'] == 'Unnamed'
    assert sheet['schema'] == str(test_schema_file)


def test_load_sheet():
    assert False
