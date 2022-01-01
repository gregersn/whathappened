import logging
from pathlib import Path
from flask import current_app
from typing import Literal

import yaml

from whathappened.character.schema import load_schema, build_from_schema

from .mechanics import CoCMechanics

from ..core import register_game

logger = logging.getLogger(__name__)


# This is not pretty
GameType = Literal["Classic (1920's)", "Modern"]
GameTypes = ["Classic (1920's)", "Modern"]
from .forms import CreateForm  # noqa F401
from .routes import view  # noqa F401

CHARACTER_TEMPLATE = 'character/coc7e/blank_character.json.jinja'
CREATE_TEMPLATE = 'character/coc7e/create.html.jinja'
CHARACTER_SCHEMA = Path(__file__).parent / '../schema/coc7e.yml'

SKILL_LIST = Path(__file__).parent / \
    '..' / 'schema' / 'coc7e_skills.yml'


def new_character(title: str,
                  gametype: GameType = "Classic (1920's)",
                  **kwargs):
    schema_data = load_schema(CHARACTER_SCHEMA)

    nc = build_from_schema(schema_data)

    mechanics = CoCMechanics(nc)
    with open(SKILL_LIST, 'r') as f:
        skill_list = yaml.safe_load(f)

    subskills = {}
    for skill in skill_list:
        if skill.get('uncommon', False):
            print(f"Skipping: {skill['name']}")
            continue

        if skill.get('modern', False) and GameType != "Modern":
            print(f"Skipping modern skill {skill['name']}")
            continue

        if parent := skill.get('parent', None):
            if parent not in subskills:
                subskills[parent] = []
            subskills[parent].append(skill)
            print(f"Found a subskill: {skill['name']}")
            continue

        mechanics.add_skill(skill['name'], start_value=skill['start_value'])

    for skill, subskills in subskills.items():
        for subskill in subskills:
            if parent := mechanics.skill(subskill['parent']):
                if parent['start_value'] == subskill['start_value']:
                    continue
            mechanics.add_subskill(
                subskill['name'], subskill['parent'], subskill['start_value'])

    return nc


register_game('coc7e', 'Call of Cthulhu TM', CoCMechanics)
