lint:
  poetry run ruff check
  poetry run mypy .

fmt:
  poetry run ruff format

test:
  poetry run pytest -k "not slow"
