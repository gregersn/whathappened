from markupsafe import Markup
from whathappened.web.campaign import forms
from whathappened.core.character.models import Character


def test_add_character_form(app):
    def blank():
        return [Character(id=1, title="foo_character")]

    with app.test_request_context("/"):
        form = forms.AddCharacterForm()

    form.character.query_factory = blank

    assert isinstance(form, forms.AddCharacterForm)
    assert form.hidden_tag() == Markup("")
    assert form.character() == Markup(
        '<select id="character" name="character"><option value="1">foo_character</option></select>'
    )
    assert form.submit() == Markup(
        '<input id="submit" name="submit" type="submit" value="Add character">'
    )
