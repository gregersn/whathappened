ACTIVATE_VENV := . venv/bin/activate

.PHONY: setup_dependencies
setup_dependencies: venv/marker

venv/marker: requirements.txt
	python3 -m venv venv
	$(ACTIVATE_VENV) && pip3 install -r requirements.txt
	touch venv/marker

.PHONY: setup
setup: setup_dependencies
	$(ACTIVATE_VENV) &&	flask db upgrade

dev:
	$(ACTIVATE_VENV) &&	FLASK_APP=whathappened FLASK_ENV=development flask run
