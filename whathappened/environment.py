from pathlib import Path
from webassets import Environment as AssetsEnvironment
from fastapi.templating import Jinja2Templates

static_folder = Path(__file__).absolute().parent / 'static'
template_folder = Path(__file__).parent / 'templates'

assets_env = AssetsEnvironment(static_folder)

templates = Jinja2Templates(directory=template_folder)
templates.env.add_extension('webassets.ext.jinja2.AssetsExtension')
templates.env.assets_environment = assets_env

assets_env.url = "/static"
assets_env.config['TYPESCRIPT_CONFIG'] = '--target ES6'
