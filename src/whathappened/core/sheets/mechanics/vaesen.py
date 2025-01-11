"""Vaesen sheet mechanics."""

import logging
from whathappened.core.sheets.mechanics.core import CharacterMechanics


logger = logging.getLogger(__name__)


class VaesenMechanics(CharacterMechanics):
    """Vaesen sheet mechanics."""

    @property
    def name(self):
        return self.parent.body["character_sheet"]["personalia"]["name"]

    @property
    def age(self):
        return self.parent.body["character_sheet"]["personalia"]["age"]

    @property
    def description(self):
        return f"{self.parent.body['character_sheet']['personalia']['archetype']}, {self.parent.body['character_sheet']['personalia']['description']}"

    @property
    def info(self):
        conditions = self.parent.body["character_sheet"]["characteristics"][
            "conditions"
        ]

        physical = conditions["physical"]
        mental = conditions["mental"]

        state = []
        broken = []

        physical_result = ""

        if physical["broken"]:
            broken.append("physically")
        elif physical["exhausted"] or physical["battered"] or physical["wounded"]:
            t = []
            if physical["exhausted"]:
                t.append("exhausted")
            if physical["battered"]:
                t.append("battered")
            if physical["wounded"]:
                t.append("wounded")

            if len(t) == 2:
                physical_result = f"{' and '.join(t)}.".capitalize()
            elif len(t) >= 3:
                physical_result = f"{', '.join(t[:2])} and {t[-1]}.".capitalize()
            else:
                physical_result = f"{', '.join(t)}.".capitalize()

        mental_result = ""

        if mental["broken"]:
            broken.append("mentally")
        elif mental["angry"] or mental["frightened"] or mental["hopeless"]:
            t = []
            if mental["angry"]:
                t.append("angry")
            if mental["frightened"]:
                t.append("frightened")
            if mental["hopeless"]:
                t.append("hopeless")

            if len(t) == 2:
                mental_result = f"Feeling {' and '.join(t)}."
            elif len(t) >= 3:
                mental_result = f"Feeling {', '.join(t[:2])} and {t[-1]}."
            else:
                mental_result = f"Feeling {', '.join(t)}."

        if physical_result:
            state.append(physical_result)

        if mental_result:
            state.append(mental_result)

        if broken:
            return " ".join(
                [f"{' and '.join(broken)} broken.".capitalize(), " ".join(state)]
            )
        if state:
            return " ".join(state)

        return "Feeling fine."


class VaesenHQMechanics(CharacterMechanics):
    """Vaesen sheet mechanics."""

    @property
    def name(self):
        return self.parent.body["character_sheet"]["information"]["name"]

    @property
    def age(self):
        return self.parent.body["character_sheet"]["information"]["development_points"]

    @property
    def description(self):
        return f"{self.parent.body['character_sheet']['information']['type_of_building']} in {self.parent.body['character_sheet']['information']['location']}"
