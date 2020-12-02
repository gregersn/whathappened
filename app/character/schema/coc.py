from jsonschema import validate

from app.character.coc import schema_file, new_character
from app.character.schema import load_schema

latest = '0.0.3'


def v002_to_v003(data):
    data = data.copy()
    data['system'] = 'coc7e'
    data['version'] = '0.0.3'
    del data['meta']['Version']
    return data


def v003_to_v002(data):
    data = data.copy()
    del data['version']
    del data['system']
    data['meta']['Version'] = "0.0.2"
    return data


def v001_to_002(data):
    data = data.copy()
    nc = new_character("Test Character", "Classic (1920's)")
    schema = load_schema(schema_file)
    validate(nc, schema=schema)

    start_values = {skill['name']: skill['start_value']
                    for skill in nc['skills']}

    for skill in nc['skills']:
        if 'subskills' in skill and skill['subskills']:
            for subskill in skill['subskills']:
                start_values[": ".join((skill['name'], subskill['name']))] = subskill['start_value']

    outskills = []
    skill_index = {}

    for skill in data['skills']:
        if skill['name'] in start_values:
            skill['start_value'] = start_values[skill['name']]
        else:
            skill['start_value'] = '0'

        if 'specializations' in skill:
            skill['specializations'] = (skill['specializations'] == "true"
                                        or skill['specializations'] == "True"
                                        or skill['specializations'] is True)

        if skill['name'] not in skill_index:
            skill_index[skill['name']] = skill
            outskills.append(skill)

        if 'subskills' in skill:
            for subskill in skill['subskills']:
                fullskillname = ": ".join((skill['name'], subskill['name']))
                if fullskillname in start_values:
                    subskill['start_value'] = start_values[fullskillname]
                else:
                    subskill['start_value'] = skill['start_value']

    data['skills'] = outskills
    data['meta']['Version'] = "0.0.2"

    return data


def v002_to_001(data):
    data = data.copy()
    data['meta']['Version'] = "0.0.1"

    outskills = []
    for skill in data['skills']:
        if 'start_value' in skill:
            del skill['start_value']

        if 'subskills' in skill:
            for subskill in skill['subskills']:
                del subskill['start_value']
        if 'specializations' in skill:
            skill['specializations'] = "true" if skill['specializations'] else "false"
        outskills.append(skill)

    data['skills'] = outskills
    return data


migrations = [
    {
        'from': '0.0.1',
        'to': '0.0.2',
        'up': v001_to_002,
        'down': v002_to_001
    },
    {
        'from': '0.0.2',
        'to': '0.0.3',
        'up': v002_to_v003,
        'down': v003_to_v002
    }
]
