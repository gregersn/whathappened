import logging
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import base  # noqa: F401
from app.recipe_data import RECIPES

logger = logging.getLogger(__name__)

FIRST_SUPERUSER: EmailStr = "admin@recipeapi.com"


def init_db(db: Session) -> None:
    if FIRST_SUPERUSER:
        user = crud.user.get_by_email(db, email=FIRST_SUPERUSER)
        if not user:
            user_in = schemas.UserCreate(
                first_name="Initial",
                surname="Superuser",
                email=FIRST_SUPERUSER,
                is_superuser=True)
            user = crud.user.create(db, obj_in=user_in)
        else:
            logger.warning(
                "Skipping creating superuser. User with email {} already exists", FIRST_SUPERUSER)

        if not user.recipes:
            for recipe in RECIPES:
                recipe_in = schemas.RecipeCreate(
                    label=recipe["label"],
                    source=recipe["source"],
                    url=recipe["url"],
                    submitter_id=user.id
                )
                crud.recipe.create(db, obj_in=recipe_in)
