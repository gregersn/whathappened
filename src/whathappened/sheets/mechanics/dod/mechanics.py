from whathappened.sheets.mechanics.core import CharacterMechanics


class DoDMechanics(CharacterMechanics):
    @property
    def name(self):
        return self.parent.body["character_sheet"]["personalia"]["namn"]

    @property
    def age(self):
        return self.parent.body["character_sheet"]["personalia"]["alder"]

    @property
    def description(self):
        return f'{self.parent.body["character_sheet"]["personalia"]["slakte"]}, {self.parent.body["character_sheet"]["personalia"]["yrke"]}'
