.PHONY: format lint typecheck test validate audit sast pylint flake8 vulture changelog all

lint:
	ruff check .
	flake8 .
	pylint modules/
	vulture

format:
	black .

typecheck:
	mypy .

test:
	pytest

sast:
	bandit -c pyproject.toml -r modules/
	semgrep scan modules/ --error --quiet

audit:
	pip-audit --local
	detect-secrets scan --baseline .secrets.baseline

changelog:
	git-cliff -o CHANGELOG.md

validate:
	python scripts/validate_project.py
	python validate_project.py

all: format lint typecheck sast audit test validate

