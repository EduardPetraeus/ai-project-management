.PHONY: lint test format validate

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

test:
	python -m pytest tests/ -v --cov=src/ai_pm --cov-report=term-missing

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

validate:
	python -m ai_pm validate examples/
