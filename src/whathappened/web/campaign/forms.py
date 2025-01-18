"""Campaign related forms."""

from typing import List, Optional, Tuple
from markupsafe import Markup
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    HiddenField,
    SelectField,
    BooleanField,
    SubmitField,
    widgets,
    IntegerField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Email
from wtforms.widgets.core import HiddenInput, TextArea

from whathappened.web.forms.fields import QuerySelectField, QuerySelectMultipleField
from whathappened.web.auth.utils import current_user

from ...core.campaign.models import HandoutStatus


class CreateForm(FlaskForm):
    """Create campaign."""

    title = StringField("Title", validators=[DataRequired()])
    characters_enabled = BooleanField("Use Characters")
    npcs_enabled = BooleanField("Use NPCs")
    handouts_enabled = BooleanField("Use handouts")
    messages_enabled = BooleanField("Use messages")
    submit = SubmitField("Create")


class EditForm(CreateForm):
    """Edit campaign."""

    id = IntegerField(widget=HiddenInput())
    description = StringField("Description", widget=TextArea())
    submit = SubmitField("Save")


class DeleteForm(FlaskForm):
    """Delete campaign."""

    id = IntegerField(widget=HiddenInput())
    confirm = StringField("Confirm", validators=[DataRequired()])
    submit = SubmitField("Delete")


class InvitePlayerForm(FlaskForm):
    """Invite player to campaign."""

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Invite")


def available_characters():
    """Get avabile character for a user."""
    return current_user.profile.characters


class AddCharacterForm(FlaskForm):
    """Add character to campaign."""

    character = QuerySelectField(
        query_factory=available_characters, get_label=lambda x: x.title
    )
    submit = SubmitField("Add character")


class AddNPCForm(AddCharacterForm):
    """Add NPC to campaign."""

    visible = BooleanField("Visible", default=False)


class CampaignAssociationForm(FlaskForm):
    """Edit settings for a character-campaign association."""

    campaign_id = IntegerField(widget=HiddenInput())
    character_id = IntegerField(widget=HiddenInput())
    editable_by_gm = BooleanField("Editable by GM", default=False)
    share_with_players = BooleanField("Share with players", default=False)
    group_sheet = BooleanField("Group sheet", default=False)
    submit = SubmitField("Update settings")


class RemoveCharacterForm(FlaskForm):
    """Remove character from campaign."""

    id = IntegerField(widget=HiddenInput())
    character = IntegerField(widget=HiddenInput())
    submit = SubmitField("Remove character")


class RemovePlayerForm(FlaskForm):
    """Remove player from campaign."""

    id = IntegerField(widget=HiddenInput())
    player = IntegerField(widget=HiddenInput())
    submit = SubmitField("Remove player")


class JoinCampaignForm(FlaskForm):
    """Join campaign."""

    invite_code = HiddenField("Invite", validators=[DataRequired()])
    submit = SubmitField("Join campaign")


class EnumField(SelectField):
    """Custom enumeration field."""

    def process_data(self, value):
        if value is not None:
            value = value.name
        super(EnumField, self).process_data(value)


class PlayerListField(QuerySelectMultipleField):
    """Custom player list field."""

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

    def iter_groups(self):
        raise NotImplementedError()


class HandoutGroupForm(FlaskForm):
    """Create handout group."""

    campaign_id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Add group")


class HandoutForm(FlaskForm):
    """Create handout form."""

    campaign_id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", widget=TextArea())
    status = EnumField(
        "Status",
        choices=[(e.name, e.value) for e in HandoutStatus],
        default=HandoutStatus.draft,
    )

    group_id = SelectField(
        "Group",
        choices=[
            ("", "(none)"),
        ],
        default="",
        validate_choice=False,
    )

    submit = SubmitField("Save handout")


class DeleteHandoutForm(FlaskForm):
    """Delete handout form."""

    campaign_id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    submit = SubmitField("Delete handout")


class TableRowWidget(object):
    """Table row widget."""

    def __init__(self, with_tr_tag: bool = True):
        self.with_tr_tag = with_tr_tag

    def __call__(self, field, **kwargs):
        html = []
        if self.with_tr_tag:
            kwargs.setdefault("id", field.id)
            html.append(f"<tr {widgets.html_params(**kwargs)}>")

        hidden = ""
        for subfield in field:
            if subfield.type in ("HiddenField", "CSRFTokenField"):
                hidden += str(subfield)
            else:
                html.append(f"<td>{hidden}{subfield}</td>")
                hidden = ""
        if self.with_tr_tag:
            html.append("</tr>")
        if hidden:
            html.append(hidden)
        return Markup("".join(html))


class PlayerField(SelectMultipleField):
    widget = TableRowWidget(with_tr_tag=False)
    option_widget = widgets.CheckboxInput()


class RevealHandout(FlaskForm):
    """Show handout."""

    campaign_id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    players = QuerySelectMultipleField("Show to", get_label=lambda x: x.user.username)


class NPCTransferForm(FlaskForm):
    """Transfer NPC to player."""

    npc_id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    player = SelectField(validate_choice=False)
    submit = SubmitField("Transfer NPC")


class MessagePlayerForm(FlaskForm):
    """Send message."""

    campaign_id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    from_id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    message = StringField()
    submit = SubmitField("Send...")

    to_id = SelectField(
        "To",
        choices=[
            ("", "All"),
        ],
        validate_choice=False,
    )

    def __init__(
        self,
        *args,
        hide_to_id: bool = False,
        players: Optional[List[Tuple[int, str]]] = None,
        **kwargs,
    ):
        if players is None:
            players = []

        super().__init__(*args, **kwargs)
        if hide_to_id:
            self.to_id.widget = HiddenInput()  # type: ignore  # Not an error

        player_choices: List[Tuple[int | str, str]] = [("", "All")]
        player_choices += players
        self.to_id.choices = player_choices  # type: ignore

        assert self.to_id.choices is not None
