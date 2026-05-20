.PHONY: test lint type cov complexity all

test:
	pytest -v

cov:
	pytest --cov=src --cov=legacy test_legacy_behavior.py --cov-report=term-missing --cov-report=html

lint:
	ruff check .

type:
	mypy --strict src/ legacy.py

complexity:
	radon cc src/ legacy.py -s -a

all: lint type test cov complexity