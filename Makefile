.PHONY: install dev api build test lint format clean run docker-build docker-run

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt -r requirements-dev.txt

api:
	pip install -r requirements.txt "[api]"

build:
	python -m build

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	ruff check src/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf dist/ build/ *.egg-info/ htmlcov/ .coverage

run:
	python -m src.cli.main

interactive:
	python -m src.cli.interactive

docker-build:
	docker build -t nexus-mental-terminal:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

help:
	@echo "Available targets:"
	@echo "  install     - Install production dependencies"
	@echo "  dev         - Install development dependencies"
	@echo "  api         - Install API dependencies"
	@echo "  build       - Build package"
	@echo "  test        - Run tests with coverage"
	@echo "  lint        - Run linters"
	@echo "  format      - Format code"
	@echo "  clean       - Clean build artifacts"
	@echo "  run         - Run CLI"
	@echo "  interactive - Run interactive mode"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Start Docker containers"
	@echo "  docker-stop  - Stop Docker containers"
