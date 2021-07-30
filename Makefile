MAKEFLAGS += --jobs=4

VENV_RUN := . venv/bin/activate &&
RMRF := rm -Rf

MARKER_FILENAME := .buildmarker
FRONTEND_MARKER := frontend/$(MARKER_FILENAME)

# Default target:
.PHONY: dev_server
dev_server: frontend
	@$(VENV_RUN) FLASK_APP=whathappened FLASK_ENV=development flask run

# Install Python dependencies:
.PHONY: setup_dependencies
setup_dependencies: venv/$(MARKER_FILENAME)

venv/$(MARKER_FILENAME): requirements.txt requirements-dev.txt
	@python3 -m venv venv
	@$(VENV_RUN) pip3 install -r requirements.txt
	@$(VENV_RUN) pip3 install -r requirements-dev.txt
	@touch $@

# Initialise database:
.PHONY: setup
setup: setup_dependencies
	@$(VENV_RUN) FLASK_APP=whathappened flask db upgrade

# Install npm dependencies:
$(FRONTEND_MARKER): frontend/package.json
	@cd frontend && npm install && cd ..
	@touch $@

# Build the Flask frontend:
.PHONY: frontend
frontend: $(FRONTEND_MARKER) setup
	@$(VENV_RUN) FLASK_APP=whathappened flask main build

.PHONY: coverage
coverage: venv/$(MARKER_FILENAME) $(FRONTEND_MARKER)
	@$(VENV_RUN) pytest --cov=whathappened tests/
	@cd frontend && npm test

# Clean out build artefacts:
clean:
	$(RMRF) venv
	$(RMRF) $(FRONTEND_MARKER)
