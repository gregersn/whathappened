"""Call of Cthulhu migration functions."""

from jsonschema import validate

from whathappened.sheets.mechanics.coc7e import new_character
from whathappened.sheets.schema.build import get_schema
from whathappened.sheets.schema.utils import Migration


def v003_to_v004(data):
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
    data["system"] = "coc7e"
    data["version"] = "0.0.3"
    del data["meta"]["Version"]
    return data


def v003_to_v002(data):
    del data["version"]
    del data["system"]
    data["meta"]["Version"] = "0.0.2"
    return data


def v001_to_002(data):
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


def v004_to_v005(data):
    data["version"] = "0.0.5"
    return data


def v005_to_v004(data):
    data["version"] = "0.0.4"
    return data


def v005_to_v006(data):
    data["backstory"]["injuries"] = data["backstory"]["injurues"]
    del data["backstory"]["injurues"]
    data["version"] = "0.0.6"
    return data


def v006_to_v005(data):
    data["backstory"]["injurues"] = data["backstory"]["injuries"]
    del data["backstory"]["injuries"]
    data["version"] = "0.0.5"
    return data


def v006_to_007(data):
    data["meta"]["title"] = data["meta"]["Title"]
    del data["meta"]["Title"]
    data["meta"]["creator"] = data["meta"]["Creator"]
    del data["meta"]["Creator"]
    data["meta"]["createdate"] = data["meta"]["CreateDate"]
    del data["meta"]["CreateDate"]
    data["meta"]["gamename"] = data["meta"]["GameName"]
    del data["meta"]["GameName"]
    data["meta"]["gameversion"] = data["meta"]["GameVersion"]
    del data["meta"]["GameVersion"]
    data["meta"]["gametype"] = data["meta"]["GameType"]
    del data["meta"]["GameType"]
    data["meta"]["disclaimer"] = data["meta"]["Disclaimer"]
    del data["meta"]["Disclaimer"]

    data["version"] = "0.0.7"
    return data


def v007_to_006(data):
    data["meta"]["Title"] = data["meta"]["title"]
    del data["meta"]["title"]
    data["meta"]["Creator"] = data["meta"]["creator"]
    del data["meta"]["creator"]
    data["meta"]["CreateDate"] = data["meta"]["createdate"]
    del data["meta"]["createdate"]
    data["meta"]["GameName"] = data["meta"]["gamename"]
    del data["meta"]["gamename"]
    data["meta"]["GameVersion"] = data["meta"]["gameversion"]
    del data["meta"]["gameversion"]
    data["meta"]["GameType"] = data["meta"]["gametype"]
    del data["meta"]["gametype"]
    data["meta"]["Disclaimer"] = data["meta"]["disclaimer"]
    del data["meta"]["disclaimer"]

    data["version"] = "0.0.6"
    return data


migrations = [
    Migration("0.0.1", "0.0.2", v001_to_002, v002_to_001),
    Migration("0.0.2", "0.0.3", v002_to_v003, v003_to_v002),
    Migration("0.0.3", "0.0.4", v003_to_v004, v004_to_v003),
    Migration("0.0.4", "0.0.5"),
    Migration("0.0.5", "0.0.6", v005_to_v006, v006_to_v005),
    Migration("0.0.6", "0.0.7", v006_to_007, v007_to_006),
]
