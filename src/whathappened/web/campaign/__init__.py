from pelican.plugins.webassets.vendor.webassets.env import Environment


from . import routes  # noqa: F401,E402 isort:skip
from . import views  # noqa: F401, E402 isort:skip
from . import api  # noqa: F401, E402 isort:skip
from ...core.campaign.models import Campaign  # noqa: F401, E402 isort:skip


def register_assets(assets: Environment):
    assets.register(
        "scss_campaign",
        "scss/campaign/campaign.scss",
        filters="pyscss",
        output="css/campaign.css",
    )

    assets.register(
        "scss_handout",
        "scss/campaign/handout.scss",
        filters="pyscss",
        output="css/handout.css",
    )
