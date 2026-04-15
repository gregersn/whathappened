MAKEFLAGS += --jobs=4

VENV_PYTHON := ./.venv/bin/python3
UV_FLASK := uv run -- flask
RMRF := rm -Rf

MARKER_FILENAME := .buildmarker
FRONTEND_MARKER := frontend/$(MARKER_FILENAME)

# Default target:
.PHONY: dev_server
dev_server: frontend
	@FLASK_APP=src/whathappened.web FLASK_DEBUG=1 $(UV_FLASK) run --extra-files ./src/whathappened/static/manifest.json

# Install Python dependencies:
.PHONY: setup_dependencies
setup_dependencies: .venv/$(MARKER_FILENAME) $(FRONTEND_MARKER)

.venv/$(MARKER_FILENAME): pyproject.toml
	@uv sync
	@touch $@

# Initialise database:
.PHONY: setup
setup: setup_dependencies
	@FLASK_APP=src/whathappened.web FLASK_DEBUG=1 $(UV_FLASK) db upgrade

# Install npm dependencies:
$(FRONTEND_MARKER): package.json
	@npm install
	@touch $@

# Build the Flask frontend:
.PHONY: frontend
frontend: $(FRONTEND_MARKER) setup
	@FLASK_APP=src/whathappened.web FLASK_DEBUG=1 $(UV_FLASK) main build

.PHONY: coverage
coverage: .venv/$(MARKER_FILENAME) $(FRONTEND_MARKER)
	@uv run pytest --cov=whathappened tests/
	@npm test

.PHONY: dist
dist: setup_dependencies
	$(RMRF) build dist
	$(RMRF) src/whathappened/static/js/
	$(RMRF) src/whathappened/static/css/
	npm run dist
	@FLASK_APP=src/whathappened.web uv run -- flask assets build
	@$(VENV_PYTHON) -m build


.PHONY: update_schemas
update_schemas:
	cp tests/games/schemas/current/* tests/games/schemas/expected/

.PHONY: update_sheets
update_sheets:
	cp tests/games/sheets/current/* tests/games/sheets/expected/

# Clean out build artefacts:
clean:
	$(RMRF) .venv
	$(RMRF) $(FRONTEND_MARKER)
