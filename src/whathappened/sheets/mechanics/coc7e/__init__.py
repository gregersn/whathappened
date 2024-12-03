import json
import time
from pathlib import Path
from typing import Literal, Optional
import jinja2


GameType = Literal["Classic (1920's)", "Modern"]
GameTypes = ["Classic (1920's)", "Modern"]
current_folder = Path(__file__).parent
CHARACTER_TEMPLATE = "character/coc7e/blank_character.json.jinja"


def new_character(
    title: str,
    gametype: GameType = "Classic (1920's)",
    timestamp: Optional[float] = None,
    **kwargs,
):
    """Create new CoC7e character."""
    templateloader = jinja2.FileSystemLoader(
        searchpath=current_folder / "../../templates/"
    )
    templateenv = jinja2.Environment(loader=templateloader)
    template = templateenv.get_template(CHARACTER_TEMPLATE)
    gtype = gametype
    return json.loads(
        template.render(title=title, timestamp=timestamp or time.time(), gametype=gtype)
    )
