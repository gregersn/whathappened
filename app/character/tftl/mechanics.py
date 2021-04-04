import os

from ..core import CharacterMechanics
from ..schema import validate
CHARACTER_SCHEMA = os.path.join(
    os.path.dirname(__file__), '../schema/tftl.json')


class TftlMechanics(CharacterMechanics):
    def validate(self):
        return validate(self.parent.body, CHARACTER_SCHEMA)

    def version(self):
        return '0.0.1'

    @property
    def name(self):
        return self.parent.body['character_sheet']['personalia']['name']

    @property
    def age(self):
        return self.parent.body['character_sheet']['personalia']['age']

    @property
    def description(self):
        return self.parent.body['character_sheet']['personalia']['type']

    def portrait(self):
        return self.parent.body['character_sheet']['personalia'].get('portrait', None)

    def skill(self, *args, **kwargs):
        return "Nope"

    def relationships(self, who: str):
        return self.parent.body['character_sheet']['relationships'][who]

    def items(self):
        return self.parent.body['character_sheet']['items']

    def set_portrait(self, data):
        self.parent.body['character_sheet']['personalia']['portrait'] = data
        return self.portrait
