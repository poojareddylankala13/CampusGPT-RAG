.PHONY: format lint typecheck test validate all

lint:
	ruff check .

format:
	black .

typecheck:
	mypy .

test:
	pytest

validate:
	python scripts/validate_project.py

all: format lint typecheck test validate
