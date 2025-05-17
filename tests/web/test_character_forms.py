from whathappened.web.character.forms import ImportForm


def test_edit_json(test_app):
    form = ImportForm()
    assert not form.validate()
