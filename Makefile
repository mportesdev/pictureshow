.PHONY: build test testall clean cleandist

build: cleandist
	poetry build

test:
	tox run -m latest

testall:
	tox run -m python pypy code

clean: cleandist
	rm -rf src/pictureshow/__pycache__/ tests/__pycache__/
	rm -rf .tox/ htmlcov/
	rm -f .coverage coverage.xml

cleandist:
	rm -rf dist/
