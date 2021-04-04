
"""Test functions related to Star Wars WEG D6."""
import os
import yaml
import pytest

from jsonschema import validate

from app.character.schema import load_schema

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def test_validate_tftl_schema():
    schema = load_schema(os.path.join(os.path.dirname(__file__),
                                      '../schema/character_sheet.yaml'))

    from app.character.tftl import CHARACTER_SCHEMA
    with open(CHARACTER_SCHEMA, 'r') as f:
        data = yaml.safe_load(f)

        validate(data, schema=schema)
