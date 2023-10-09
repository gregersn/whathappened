# Adding new models to the database.

1. Define models in code.
1. Create migration file
    - `PYTHONPATH='.' alembic -c ./whathappened/migrations/alembic.ini revision --autogenerate -m 'Migration message'`
    - `PYTHONPATH='.' alembic -c ./whathappened/migrations/alembic.ini upgrade head`
1. Check that things work as expected.
1. Add migration file to repository.
