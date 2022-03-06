from typing import Any, Optional
from pathlib import Path

from pydantic import BaseModel

from sqlalchemy.orm import Session

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import Response

from fastapi import FastAPI, APIRouter, Query, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from app.schemas.recipe import RecipeSearchResults, Recipe, RecipeCreate
from app.recipe_data import RECIPES
from app import crud
from app import deps

from webassets import Environment as AssetsEnvironment, Bundle
from webassets.ext.jinja2 import AssetsExtension

BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))
app = FastAPI(title="WhatHappened? API", openapi_url="/openapi.json")

app.mount("/static",
          StaticFiles(directory="whathappened/static"),
          name="static")

assets = AssetsEnvironment('templates', 'static')
TEMPLATES.env.directory = "foo"
TEMPLATES.env.url = "bar"
TEMPLATES.env.add_extension(AssetsExtension)
TEMPLATES.env.assets_environment = assets
# assets._named_bundles = {}
# assets.init_env(TEMPLATES.env)

scss = Bundle('scss/main.scss', filters='pyscss', output='css/all.css')
assets.register('scss_all', scss)

SECRET = "super-secret-key"
manager = LoginManager(SECRET, '/login', use_cookie=True)

api_router = APIRouter()

DB = {'users': {'gregersn@gmail.com': {'name': "Greger", 'password': 'test'}}}


@app.get('/', status_code=200)
def root(request: Request, db: Session = Depends(deps.get_db)) -> Any:
    # if current user is authenticated
    # return redirect to user profile

    return TEMPLATES.TemplateResponse("main/index.html.jinja",
                                      {'request': request})


@manager.user_loader()
def query_user(user_id: str):
    return DB['users'].get(user_id)


@api_router.post("/login")
def login(response: Response, data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = query_user(email)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data={'sub': email})
    manager.set_cookie(response, access_token)
    return {'token': access_token}


"""
@api_router.get("/", status_code=200)
def root(request: Request, db: Session = Depends(deps.get_db), user=Depends(manager)) -> Any:
    recipes = crud.recipe.get_multi(db=db, limit=10)
    return TEMPLATES.TemplateResponse("index.html",
                                      {"request": request,
                                       "recipes": recipes})
"""


@api_router.get("/recipe/{recipe_id}", status_code=200, response_model=Recipe)
def fetch_recipe(*, recipe_id: int, db: Session = Depends(deps.get_db)) -> Any:
    """
    Fetch a single recipe by ID
    """

    # 4
    result = crud.recipe.get(db=db, id=recipe_id)
    if not result:
        raise HTTPException(status_code=404,
                            detail=f"Recipe with ID {recipe_id} not found")

    return result


# 3
@api_router.get("/search/",
                status_code=200,
                response_model=RecipeSearchResults)
def search_recipes(
    *,
    keyword: Optional[str] = Query(None, min_length=3, example='chicken'),
    max_results: int = 10,
    db: Session = Depends(deps.get_db)) -> dict:
    """
    Search for recipes based on label keyword
    """
    recipes = crud.recipe.get_multi(db=db, limit=max_results)
    if not keyword:
        # we use Python list slicing to limit results
        # based on the max_results query parameter
        return {"results": recipes}  # 6

    results = filter(lambda recipe: keyword.lower() in recipe["label"].lower(),
                     recipes)  # 7
    return {"results": list(results)[:max_results]}


@api_router.post("/recipe/", status_code=201, response_model=Recipe)
def create_recipe(
    *, recipe_in: RecipeCreate, db: Session = Depends(deps.get_db)) -> dict:
    recipe = crud.recipe.create(db=db, obj_in=recipe_in)
    return recipe


app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
