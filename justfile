set shell := ["bash", "-cu"]

setup:
	uv sync --all-extras --dev
	pre-commit install

check:
	uv run ruff check .
	uv run black --check .
	uv run mypy src tests
	uv run pytest

format:
	uv run ruff check . --fix
	uv run black .

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run black --check .
	uv run mypy src tests

docs:
	uv run mkdocs serve

docs-build:
	uv run mkdocs build --strict

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	rm -rf site htmlcov .coverage coverage.xml
