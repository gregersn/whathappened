import os
import pathlib
import yaml
from typing import Literal

from app.character.schema import load_schema, build_from_schema, validate
from .mechanics import CoCMechanics

CHARACTER_SCHEMA = os.path.join(
    os.path.dirname(__file__), '../schema/coc7e.yaml')

SKILL_LIST = pathlib.PurePath(__file__).parent / \
    '..' / 'schema' / 'coc7e_skills.yaml'

# This is not pretty
GameType = Literal["Classic (1920's)", "Modern"]
GameTypes = ["Classic (1920's)", "Modern"]


def new_character(title: str,
                  gametype: GameType = "Classic (1920's)",
                  **kwargs):
    """
    CHARACTER_SCHEMA = pathlib.PurePath(
        __file__).parent / 'schema' / 'coc7e.yaml'
    """
    schema_data = load_schema(str(CHARACTER_SCHEMA))

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
