import pathlib
from ..core import CharacterMechanics
from ..schema import validate

CHARACTER_SCHEMA = pathlib.Path(
    __file__).parent.parent.joinpath('schema/swd6.yaml')


class SWD6Mechanics(CharacterMechanics):
    def validate(self):
        return validate(self.parent.body, CHARACTER_SCHEMA)
