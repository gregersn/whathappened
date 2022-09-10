import logging
from pathlib import Path
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from fastapi import Response

from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from webassets.bundle import Bundle
from jinja2_webpack import Environment as WebpackEnvironment
from jinja2_webpack.filter import WebpackFilter

from whathappened.auth.backend import Backend
from whathappened.auth.routes import router as auth_router
from whathappened.auth import RequiresLoginException

from whathappened.config import Config
from whathappened.environment import static_folder, assets_env, templates

logger = logging.getLogger(__name__)

# Don't know if this is needed.
# assets_env._named_bundles = {}

app = FastAPI(title="What Happened?", openapi_url="/openapi.json")
app.mount("/static", StaticFiles(directory=static_folder), name="static")
app.add_middleware(SessionMiddleware, secret_key=Config.SECRET_KEY)
# app.add_middleware(AuthenticationMiddleware, backend=Backend())

scss = Bundle('scss/main.scss', filters='pyscss', output='css/all.css')
assets_env.register('scss_all', scss)

api_router = APIRouter()


@api_router.get("/hello", response_class=HTMLResponse)
async def hello(request: Request):
    return templates.TemplateResponse("hello.html.jinja", {"request": request})


logger.info("Checking config")

app.include_router(api_router)
app.include_router(auth_router)


@app.exception_handler(RequiresLoginException)
def exception_handler(request: Request, exc: RequiresLoginException) -> Response:
    """
    Redirect to login screen if someone tries to access a view that requires login.
    Workaround suggested in a GitHub comment here:
    https://github.com/tiangolo/fastapi/issues/1039#issuecomment-591661667
    """
    return RedirectResponse(url="/auth/login", status_code=302)
