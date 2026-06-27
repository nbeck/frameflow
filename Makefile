.PHONY: setup check format lint type test docs clean

setup:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"
	pre-commit install

check: format lint type test

format:
	black --check src tests
	ruff format --check src tests

lint:
	ruff check src tests

type:
	mypy src

test:
	pytest

docs:
	mkdocs serve

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov dist build *.egg-info
