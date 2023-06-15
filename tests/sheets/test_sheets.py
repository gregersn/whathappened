from whathappened.sheets.utils import create_sheet


def test_create_sheet():
    sheet = create_sheet('landf.yaml')

    assert sheet
    assert sheet['character_sheet']['name'] == "Ace"
