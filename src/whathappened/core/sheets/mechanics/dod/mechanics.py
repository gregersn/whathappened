"""DoD sheet mechanics."""

from whathappened.core.sheets.mechanics.core import CharacterMechanics


class DoDMechanics(CharacterMechanics):
    """DoD sheet mechanics."""

    @property
    def name(self):
        return self.parent.body["character_sheet"]["personalia"]["namn"]

    @property
    def age(self):
        return self.parent.body["character_sheet"]["personalia"]["alder"]

    @property
    def description(self):
        return f"{self.parent.body['character_sheet']['personalia']['slakte']}, {self.parent.body['character_sheet']['personalia']['yrke']}"
