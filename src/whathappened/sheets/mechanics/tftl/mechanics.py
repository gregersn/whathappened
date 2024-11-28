from pathlib import Path

from whathappened.sheets.schema.build import validate

from ..core import CharacterMechanics

CHARACTER_SCHEMA = Path(__file__).parent.parent.parent / "schema" / "tftl.json"
assert CHARACTER_SCHEMA.is_file(), CHARACTER_SCHEMA


class TftlMechanics(CharacterMechanics):
    def validate(self):
        return validate(self.parent.body, "tftl")

    def version(self):
        return "0.0.1"

    @property
    def name(self):
        return self.parent.body["personalia"]["name"]

    @property
    def age(self):
        return self.parent.body["personalia"]["age"]

    @property
    def description(self):
        return self.parent.body["personalia"]["type"]

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
