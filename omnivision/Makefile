# OmniVision Makefile
# Usage examples:
#   make setup
#   make train
#   make run
#   make clean

PYTHON = python
VENV = .venv

setup:
	@echo "Setting up environment..."
	$(PYTHON) -m venv $(VENV)
	$(VENV)/Scripts/pip install --upgrade pip
	$(VENV)/Scripts/pip install -r requirements.txt

train:
	@echo "Training OmniVision..."
	$(VENV)/Scripts/python -m src.train --config config.yaml --out ./models/ckpt

run:
	@echo "Launching OmniVision Desktop..."
	$(VENV)/Scripts/python run_desktop.py

run-sh:
	@echo "Launching OmniVision (Linux/Mac)..."
	$(VENV)/bin/python run_desktop.py

clean:
	@echo "Cleaning build artifacts..."
	-rm -rf __pycache__ */__pycache__ *.pyc .pytest_cache
	-rm -rf ./models/ckpt
