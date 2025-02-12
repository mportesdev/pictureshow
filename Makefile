.PHONY: build tag develop test testall clean cleandist change

build: cleandist
	poetry build

tag:
	git tag $$(poetry version --short)

develop:
	poetry install --with=develop

test:
	poetry run pytest

testall:
	tox run -m python pypy code

clean: cleandist
	rm -rf src/pictureshow/__pycache__/ tests/__pycache__/
	rm -rf .tox/ .pytest_cache/ htmlcov/
	rm -f .coverage coverage.xml

cleandist:
	rm -rf dist/

change:
	mkdir -p changelog.d
	tox run -e changelog -- create
