#!/usr/bin/env bash

python3 -m app.backend_pre_start

PYTHONPATH=. alembic upgrade head

python3 -m app.initial_data
