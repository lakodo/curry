.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install


.PHONY: build-css
build-css: ## parse templates files of the server to let tailwind generate the final css file
	@echo "🚀 Opening server folder and Running npm command build:css"
	@cd curry/server && npm run build:css

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv sync --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry .

.PHONY: run-demo
run-demo: ## Run a demo code
	@echo "🚀 Running demo code"
	@uv run python curry/demos/existing_functions/demo.py

.PHONY: run-server
run-server: ## Run the fastapi app server
	@echo "🚀 Running server"
	@uv run fastapi dev curry/server/main.py


.PHONY: run-local-dask-scheduler
run-local-dask-scheduler: ## Run a local Dask scheduler
	@echo "🚀 Running a local Dask scheduler"
	@uv run python curry/schedulers/dask/local_scheduler.py

.PHONY: run-local-dask-workers
run-local-dask-workers: ## Run a local Dask scheduler (with auto nb)
	@echo "🚀 Running local Dask workers (with auto nb)"
	@uv run dask worker --nworkers=4 --nthreads=10 --no-dashboard tcp://127.0.0.1:18000

.PHONY: run-local-dask-test
run-local-dask-test: ## Run a local Dask scheduler (with auto nb)
	@echo "🚀 Running local Dask workers (with auto nb)"
	@uv run python curry/schedulers/dask/local_test.py


.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## clean build artifacts
	@rm -rf dist

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing: Dry run."
	@uvx --from build pyproject-build --installer uv
	@echo "🚀 Publishing."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: alembic-check
alembic-check: ## Check the current database state compared to the alembic migrations
	@echo "🚀 Running alembic check"
	@uv run alembic check


.PHONY: alembic-autogenerate
alembic-autogenerate: ## Generate a migration script
	@echo "🚀 Running alembic revision autogenerate with message."
	@uv run alembic revision --autogenerate -m "$(message)"

.PHONY: alembic-upgrade
alembic-upgrade: ## Upgrade the database to the latest version
	@echo "🚀 Running alembic upgrade head"
	@uv run alembic upgrade head

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
