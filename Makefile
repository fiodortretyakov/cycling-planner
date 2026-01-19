.PHONY: setup run test smoke-claude

VENV := .venv
PY := $(VENV)/bin/python

setup:
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) -m uvicorn src.main:app --reload

test:
	$(PY) -m pytest tests -v --tb=short --cov=src --cov-report=term --cov-report=xml

smoke-claude:
	$(PY) scripts/smoke_anthropic.py
