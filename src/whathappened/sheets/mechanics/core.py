"""Core mechanics for manipulating character sheet."""

from functools import reduce
import logging
from typing import Dict, Optional, Type
import base64
import io
from PIL import Image

from whathappened.sheets.schema.base import Gametag
from whathappened.sheets.schema.build import (
    get_module,
    get_schema,
    build_from_schema,
    validate,
)

logger = logging.getLogger(__name__)

GAMES = {}

MECHANICS = {}

GameSystems = []

CHARACTER_SHEET_TEMPLATE = ""


def fix_image(imagedata: str) -> str:
    """Convert image to right size and bith depth."""
    imagetype, imagedata = imagedata.split(",")  # pylint: disable=unused-variable
    decoded = base64.b64decode(imagedata)
    buf = io.BytesIO(decoded)
    img = Image.open(buf).convert("RGB")
    img.thumbnail((192, 192))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


class CharacterMechanics:
    """Base class for character mechanics."""

    def __init__(self, parent):
        self.parent = parent

    def game(self):
        """Get game specific stuff."""
        raise NotImplementedError

    def validate(self, *args, **kwargs):
        """Validate character sheet data against game system."""
        return validate(self.parent.body, self.parent.system)

    @property
    def name(self) -> str:
        """Name of the character."""
        logger.error("name: Not implemented")
        return "Unknown property, name"

    @property
    def age(self) -> Optional[str]:
        """Age of character."""
        logger.error("age: Not implemented")
        return "Unknown property, age"

    @property
    def description(self) -> str:
        """Character description."""
        logger.error("description: Not implemented")
        return "Unknown property, description"

    @property
    def portrait(self):
        """Character portrait."""
        if res := self.attribute("character_sheet.personalia.portrait"):
            return res

        if res := self.attribute("character_sheet.portrait"):
            return res

        if res := self.attribute("character_sheet.information.picture"):
            return res

        logger.error("portrait: Not implemented")
        return None

    def store_data(self):
        """Store character data."""
        return

    def skill(self, skill, subskill=None):
        """Manipulate skill."""
        raise NotImplementedError

    def skills(self, *args):
        """Get skills."""
        raise NotImplementedError

    def set_portrait(self, data: str):
        """Set character portrait."""
        raise NotImplementedError

    def attribute(self, *args):
        """Get an attribute."""
        path = args[0]
        logger.debug("Getting attribute for: %s", path)

        def reducer(source, selector):
            if isinstance(source, list):
                return source[int(selector)]
            return source[selector] if source is not None else None

        try:
            val = reduce(
                reducer,
                path.split("."),
                self.parent.body,
            )
        except KeyError:
            # TODO: This is a bad hack
            logger.error("Could not resolve: %s in %s", path, self.parent)
            return None

        return val

    def set_attribute(self, attribute: Dict):
        """Set an attribute."""
        if attribute.get("category", None) == "skill":
            logger.debug("Set a skill")
            datatype = attribute.get("type", "string")
            skill = attribute["field"]
            subfield = attribute.get("subfield", None)
            value = attribute.get("value")

            if datatype == "number" and not isinstance(value, int):
                value = None

            skill = self.skill(skill, subfield)
            skill["value"] = value

        elif attribute.get("type", None) == "skillcheck":
            logger.debug("Check a skill")
            skill = attribute["field"]
            subfield = attribute.get("subfield", None)
            check = attribute.get("value", False)
            skill = self.skill(skill, subfield)
            skill["checked"] = check

        elif attribute.get("type", None) == "occupationcheck":
            logger.debug("Mark occupation skill")
            skill = attribute["field"]
            subfield = attribute.get("subfield", None)
            check = attribute.get("value", False)
            skill = self.skill(skill, subfield)
            skill["occupation"] = check

        elif attribute.get("type", None) == "portrait":
            logger.debug("Set portrait")
            data = attribute.get("value", None)
            if data is not None:
                # self.set_portrait(fix_image(data))
                self.set_attribute(
                    {"value": fix_image(data), "field": attribute.get("field", None)}
                )
        else:
            logger.debug("Set '%s' to '%s'", attribute["field"], attribute["value"])

            def reducer(source, selector):
                if isinstance(source, list):
                    idx = int(selector)
                    if idx < 0:
                        raise NotImplementedError("Index is less than 1")
                    return source[int(selector)]
                return source[selector] if source is not None else None

            s = reduce(reducer, attribute["field"].split(".")[:-1], self.parent.body)
            accessor = attribute["field"].split(".")[-1]
            if isinstance(s, list):
                idx = int(accessor)
                if idx < 0:
                    s.append(attribute["value"])
                else:
                    s[idx] = attribute["value"]
            elif s is not None:
                s[accessor] = attribute["value"]
                return s.get("name", None)
            else:
                logger.error("Unknown object manipulation: %s", type(s))

    def add_skill(self, skillname: str, value: int = 1):
        """Add skill."""
        if self.skill(skillname) is not None:
            raise ValueError(f"Skill {skillname} already exists.")

        self.parent.data["character_sheet"]["skills"].append(
            {"name": skillname, "value": value, "start_value": value}
        )
        if isinstance(self.parent.data["character_sheet"]["skills"], list):
            self.parent.data["character_sheet"]["skills"].sort(key=lambda x: x["name"])

    def add_subskill(self, name: str, parent: str):
        """Add subskill."""
        value = self.skill(parent)["value"]
        start_value = self.skill(parent)["start_value"]
        logger.debug("Try to add subskill")
        logger.debug("Name: %s, parent %s, value %s", name, parent, value)
        if self.skill(parent, name) is not None:
            raise ValueError(f"Subskill {name} in {parent} already exists.")

        skill = self.skill(parent)
        if "subskills" not in skill:
            skill["subskills"] = []
        skill["subskills"].append(
            {"name": name, "value": value, "start_value": start_value}
        )


def register_game(
    tag: Gametag, name: str, mechanics: Type[CharacterMechanics] = CharacterMechanics
):
    """Register a game system."""
    global GameSystems
    GAMES[tag] = name
    MECHANICS[tag] = mechanics

    GameSystems.clear()
    GameSystems += [(k, v) for k, v in GAMES.items()]


def new_character(title: str, system: Optional[Gametag] = None, **kwargs):
    """Create new character."""
    if system is None:
        raise SyntaxError("new_character: System not specified")

    module = get_module(system)
    if module is not None:
        return module.CharacterSheet(title=title).model_dump()

    logger.debug("Getting schema")
    schema_data = get_schema(system)
    new_character_data = build_from_schema(schema_data)
    new_character_data["title"] = title

    return new_character_data
