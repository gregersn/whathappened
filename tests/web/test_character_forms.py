from whathappened.web.character.forms import ImportForm


def test_edit_json(app):
    form = ImportForm()
    assert not form.validate()
