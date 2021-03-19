import os
from ..core import CharacterMechanics
from ..schema import validate

schema_file = os.path.join(os.path.dirname(__file__), '../schema/sw.yaml')


class SWD6Mechanics(CharacterMechanics):
    def validate(self):
        return validate(self.parent.body, schema_file)
