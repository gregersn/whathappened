from whathappened.sheets.schema.build import validate

from ..core import CharacterMechanics


class TftlMechanics(CharacterMechanics):
    @property
    def name(self):
        return self.parent.body["personalia"]["name"]

    @property
    def age(self):
        return self.parent.body["personalia"]["age"]

    @property
    def description(self):
        return self.parent.body["personalia"]["type"]

    @property
    def portrait(self):
        return self.parent.body["personalia"].get("portrait", None)

    def skill(self, *args, **kwargs):
        return "Nope"

    def relationships(self, who: str):
        return self.parent.body["relationships"][who]

    def items(self):
        return self.parent.body["items"]

    def set_portrait(self, data):
        self.parent.body["personalia"]["portrait"] = data
        return self.portrait
