from pathlib import Path

from ..core import CharacterMechanics
from ..schema import validate
CHARACTER_SCHEMA = Path(__file__).parent / '../schema/tftl.json'


class TftlMechanics(CharacterMechanics):
    def validate(self):
        return None
        return validate(self.parent.body, CHARACTER_SCHEMA)

    def version(self):
        return '0.0.1'

    @property
    def name(self):
        return self.data['personalia']['name']

    @property
    def age(self):
        return self.data['personalia']['age']

    @property
    def description(self):
        return self.data['personalia']['type']

    def portrait(self):
        return self.data['personalia'].get('portrait', None)

    def skill(self, *args, **kwargs):
        return "Nope"

    def relationships(self, who: str):
        return self.data['relationships'][who]

    def items(self):
        return self.data['items']

    def set_portrait(self, data):
        self.data['personalia']['portrait'] = data
        return self.portrait
