test:
    uv run pytest

lint:
    uv run ruff check .

fmt:
    uv run ruff format .

run:
    uv run python -c "from ymse import run; run()"
