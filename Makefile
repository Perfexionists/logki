help:
	@echo "Logki - Log Analysis Kit"
	@echo ""
	@echo "For best developer experience, make sure to use a virtual environment."
	@echo "For more information about how to contribute, see the CONTRIBUTING file."
	@echo ""
	@echo "Main commands:"
	@echo "    dev           Install all dependencies and set up an editable environment"
	@echo "    install       Install the project"
	@echo "    lint          Run linters (black, pylint)"
	@echo "    check         Run static type checker (mypy)"
	@echo "    test          Run tests with pytest"
	@echo "    release       Generate sdist and wheel"

.PHONY: help dev install check lint test release docs docs-release docs-all docs-html docs-dirhtml docs-latex

# Base build requirements are not installed automatically.
# Inspired by https://meson-python.readthedocs.io/en/latest/how-to-guides/editable-installs.html
dev:
	$(info [INFO] Make sure you're using a virtual environment for development)
	python3 -m pip install --no-build-isolation --config-settings=editable-verbose=true --config-settings=setup-args=-Dbuildtype=debug --editable .[test,typing,lint,docs]

install:
	pip3 install .

check:
	python3 -m mypy ./logki/

lint:
	python3 -m black -q ./logki/
	python3 -m pylint --jobs 0 ./logki/ || true

test:
	python3 -m pytest --durations=10 --cov=./ --cov-report term-missing:skip-covered ./tests/

# In the CI environemnt we want to see all the tests and want coverage report to be in XML
# because the results are being uploaded to Codecov.
test-ci:
	python3 -m pytest --cov=./ --cov-report xml --cov-report term-missing:skip-covered ./tests/

release:
	python3 -m build