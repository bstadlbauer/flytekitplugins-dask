.PHONY: setup
setup:
	poerty install
	poetry run pre-commit install
