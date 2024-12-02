"""Call of Cthulhu migration functions."""

from jsonschema import validate

from whathappened.sheets.mechanics.coc7e import new_character
from whathappened.sheets.schema.build import get_schema

LATEST = "0.0.5"


def v004_to_v005(data):
    data = data.copy()
    data["version"] = "0.0.5"
    return data


def v005_to_v004(data):
    data = data.copy()
    data["version"] = "0.0.4"
    return data


def v003_to_v004(data):
    data = data.copy()
    data["version"] = "0.0.4"
    for k, v in data["characteristics"].items():
        data["characteristics"][k] = int(v)

    for skill in data["skills"]:
        value = skill["value"]
        try:
            value = int(skill["value"], 10)
        except ValueError:
            value = None
        skill["value"] = value

        start_value = skill["start_value"]
        try:
            start_value = int(start_value, 10)
        except ValueError:
            pass

        skill["start_value"] = start_value

        if "subskills" in skill:
            for subskill in skill["subskills"]:
                subskill["value"] = int(subskill["value"], 10)

    for weapon in data["weapons"]:
        value = weapon["regular"]
        try:
            value = int(value, 10)
        except ValueError:
            value = 0
        weapon["regular"] = value

        value = weapon["ammo"]
        try:
            value = int(value, 10)
        except ValueError:
            pass
        weapon["ammo"] = value

        value = weapon["malf"]
        try:
            value = int(value, 10)
        except ValueError:
            pass
        weapon["malf"] = value

    return data


def v004_to_v003(data):
    data = data.copy()
    data["version"] = "0.0.3"
    for k, v in data["characteristics"].items():
        data["characteristics"][k] = str(v)

    for skill in data["skills"]:
        skill["value"] = str(skill["value"])
        if "subskills" in skill:
            for subskill in skill["subskills"]:
                subskill["value"] = str(subskill["value"])

    for weapon in data["weapons"]:
        value = weapon["regular"]
        weapon["regular"] = str(value)

        value = weapon["ammo"]
        weapon["ammo"] = str(value)

        weapon["malf"] = str(weapon["malf"])

    return data


def v002_to_v003(data):
    data = data.copy()
    data["system"] = "coc7e"
    data["version"] = "0.0.3"
    del data["meta"]["Version"]
    return data


def v003_to_v002(data):
    data = data.copy()
    del data["version"]
    del data["system"]
    data["meta"]["Version"] = "0.0.2"
    return data


def v001_to_002(data):
    data = data.copy()
    nc = new_character("Test Character", "Classic (1920's)")
    schema = get_schema("coc7e")
    validate(nc, schema=schema)

    start_values = {skill["name"]: str(skill["start_value"]) for skill in nc["skills"]}

    for skill in nc["skills"]:
        if "subskills" in skill and skill["subskills"]:
            for subskill in skill["subskills"]:
                start_values[": ".join((skill["name"], subskill["name"]))] = str(
                    subskill["start_value"]
                )

    outskills = []
    skill_index = {}

    for skill in data["skills"]:
        if skill["name"] in start_values:
            skill["start_value"] = start_values[skill["name"]]
        else:
            skill["start_value"] = "0"

        if "specializations" in skill:
            skill["specializations"] = (
                skill["specializations"] == "true"
                or skill["specializations"] == "True"
                or skill["specializations"] is True
            )

        if skill["name"] not in skill_index:
            skill_index[skill["name"]] = skill
            outskills.append(skill)

        if "subskills" in skill:
            for subskill in skill["subskills"]:
                fullskillname = ": ".join((skill["name"], subskill["name"]))
                if fullskillname in start_values:
                    subskill["start_value"] = start_values[fullskillname]
                else:
                    subskill["start_value"] = skill["start_value"]

    data["skills"] = outskills
    data["meta"]["Version"] = "0.0.2"

    return data


def v002_to_001(data):
    data = data.copy()
    data["meta"]["Version"] = "0.0.1"

    outskills = []
    for skill in data["skills"]:
        if "start_value" in skill:
            del skill["start_value"]

        if "subskills" in skill:
            for subskill in skill["subskills"]:
                del subskill["start_value"]
        if "specializations" in skill:
            skill["specializations"] = "true" if skill["specializations"] else "false"
        outskills.append(skill)

    data["skills"] = outskills
    return data


migrations = [
    {
        "from": "0.0.1",
        "to": "0.0.2",
        "up": v001_to_002,
        "down": v002_to_001,
    },
    {
        "from": "0.0.2",
        "to": "0.0.3",
        "up": v002_to_v003,
        "down": v003_to_v002,
    },
    {
        "from": "0.0.3",
        "to": "0.0.4",
        "up": v003_to_v004,
        "down": v004_to_v003,
    },
    {
        "from": "0.0.4",
        "to": "0.0.5",
        "up": v004_to_v005,
        "down": v005_to_v004,
    },
]
