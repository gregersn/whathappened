"""Vaesen sheet mechanics."""

from whathappened.sheets.mechanics.core import CharacterMechanics


class VaesenMechanics(CharacterMechanics):
    """Vaesen sheet mechanics."""

    @property
    def name(self):
        return self.parent.body["character_sheet"]["personalia"]["name"]

    @property
    def age(self):
        return self.parent.body["character_sheet"]["personalia"]["age"]

    @property
    def description(self):
        return f'{self.parent.body["character_sheet"]["personalia"]["archetype"]}, {self.parent.body["character_sheet"]["personalia"]["description"]}'


class VaesenHQMechanics(CharacterMechanics):
    """Vaesen sheet mechanics."""

    @property
    def name(self):
        return self.parent.body["character_sheet"]["information"]["name"]

    @property
    def age(self):
        return self.parent.body["character_sheet"]["information"]["development_points"]

    @property
    def description(self):
        return f'{self.parent.body["character_sheet"]["information"]["type_of_building"]} in {self.parent.body["character_sheet"]["information"]["location"]}'
