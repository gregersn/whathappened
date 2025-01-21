from whathappened.web.character.forms import ImportForm


def test_edit_json(app):
    form = ImportForm()
    assert not form.validate()

    form.body.data = "{}"
    form.title.data = "test import form"
    assert form.validate(), form.errors
