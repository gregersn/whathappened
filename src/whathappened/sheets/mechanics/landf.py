"""Lasers and feelings sheet mechanics."""

from whathappened.sheets.mechanics.core import CharacterMechanics


class LandfMechanics(CharacterMechanics):
    """Lasers and feelings sheet mechanics."""

    @property
    def name(self):
        return self.parent.body["character_sheet"]["name"]

    @property
    def age(self):
        return None

    @property
    def description(self):
        return f'{self.parent.body["character_sheet"]["style"]}, {self.parent.body["character_sheet"]["role"]}'
