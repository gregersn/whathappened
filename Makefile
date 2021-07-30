MAKEFLAGS += --jobs=4

VENV_PYTHON := ./venv/bin/python3
VENV_FLASK := ./venv/bin/flask
VENV_PIP := ./venv/bin/pip3
VENV_RUN := . venv/bin/activate &&
RMRF := rm -Rf

MARKER_FILENAME := .buildmarker
FRONTEND_MARKER := frontend/$(MARKER_FILENAME)

# Default target:
.PHONY: dev_server
dev_server: frontend
	@FLASK_APP=whathappened FLASK_ENV=development $(VENV_FLASK) run

# Install Python dependencies:
.PHONY: setup_dependencies
setup_dependencies: venv/$(MARKER_FILENAME)

venv/$(MARKER_FILENAME): requirements.txt requirements-dev.txt
	@python3 -m venv venv
	@$(VENV_PIP) install -r requirements.txt
	@$(VENV_PIP) install -r requirements-dev.txt
	@touch $@

# Initialise database:
.PHONY: setup
setup: setup_dependencies
	@FLASK_APP=whathappened FLASK_ENV=development $(VENV_FLASK) db upgrade

# Install npm dependencies:
$(FRONTEND_MARKER): frontend/package.json
	@cd frontend && npm install && cd ..
	@touch $@

# Build the Flask frontend:
.PHONY: frontend
frontend: $(FRONTEND_MARKER) setup
	@FLASK_APP=whathappened FLASK_ENV=development $(VENV_FLASK) main build

.PHONY: coverage
coverage: venv/$(MARKER_FILENAME) $(FRONTEND_MARKER)
	@$(VENV_PYTHON) pytest --cov=whathappened tests/
	@cd frontend && npm test

# Clean out build artefacts:
clean:
	$(RMRF) venv
	$(RMRF) $(FRONTEND_MARKER)
