from whathappened.sheets.utils import create_sheet


def test_create_sheet():
    sheet = create_sheet('landf')

    assert sheet
