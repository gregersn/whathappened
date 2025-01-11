MAKEFLAGS += --jobs=4

VENV_PYTHON := ./.venv/bin/python3
VENV_FLASK := ./.venv/bin/flask
VENV_PIP := ./.venv/bin/pip3
VENV_RUN := . .venv/bin/activate &&
RMRF := rm -Rf

MARKER_FILENAME := .buildmarker
FRONTEND_MARKER := frontend/$(MARKER_FILENAME)

# Default target:
.PHONY: dev_server
dev_server: frontend
	@FLASK_APP=src/whathappened FLASK_DEBUG=1 $(VENV_FLASK) run --extra-files ./src/whathappened/static/manifest.json

# Install Python dependencies:
.PHONY: setup_dependencies
setup_dependencies: .venv/$(MARKER_FILENAME) $(FRONTEND_MARKER)

.venv/$(MARKER_FILENAME): requirements.txt requirements-dev.txt
	@python3 -m venv .venv
	@$(VENV_PIP) install -r requirements.txt
	@$(VENV_PIP) install -r requirements-dev.txt
	@$(VENV_PIP) install -e .
	@touch $@

# Initialise database:
.PHONY: setup
setup: setup_dependencies
	@FLASK_APP=src/whathappened FLASK_DEBUG=1 $(VENV_FLASK) db upgrade

# Install npm dependencies:
$(FRONTEND_MARKER): frontend/package.json
	@cd frontend && npm install && cd ..
	@touch $@

# Build the Flask frontend:
.PHONY: frontend
frontend: $(FRONTEND_MARKER) setup
	@FLASK_APP=src/whathappened FLASK_DEBUG=1 $(VENV_FLASK) main build

.PHONY: coverage
coverage: .venv/$(MARKER_FILENAME) $(FRONTEND_MARKER)
	@$(VENV_PYTHON) -m pytest --cov=whathappened tests/
	@cd frontend && npm test

.PHONY: dist
dist: setup_dependencies
	$(RMRF) build dist
	$(RMRF) src/whathappened/static/js/
	$(RMRF) src/whathappened/static/css/
	cd frontend; npm run dist
	@FLASK_APP=src/whathappened $(VENV_FLASK) assets build
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
