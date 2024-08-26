.PHONY: build test testall clean cleandist

build: cleandist
	poetry build

test:
	tox run -e py312 --skip-pkg-install

testall:
	tox run
	tox run -e coverage,code

clean: cleandist
	rm -rf src/pictureshow/__pycache__/ tests/__pycache__/
	rm -rf .tox/ htmlcov/
	rm -f .coverage coverage.xml

cleandist:
	rm -rf dist/
