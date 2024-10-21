# Changelog

<!-- scriv-insert-here -->

<a id='changelog-0.13.0'></a>
## 0.13.0 — 2024-10-22

### Breaking changes

- Library API: the `fill_area` keyword parameter renamed to `fill_cell`
- CLI: the `-a`/`--fill-area` option renamed to `-c`/`--fill-cell`

### Added

- CLI: errors caught when reading picture files are now being logged for later inspection
- support for Python 3.13

### Removed

- support for Python 3.8
- support for PyPy 3.9


<a id='changelog-0.12.1'></a>
## 0.12.1 — 2023-12-08

### Added

- Library API: the optional `bg_color` parameter to `PictureShow.save_pdf` and `pictures_to_pdf` to specify page background color (#29)
- CLI: the `--bg-color` option to set page background color (#29)


<a id='changelog-0.12.0'></a>
## 0.12.0 — 2023-12-04

### Changed

- Library API: the `page_size`, `landscape`, `margin`, `layout`, `stretch_small`, `fill_area` and `force_overwrite`
  parameters to `PictureShow.save_pdf` are now keyword-only (#28)


<a id='changelog-0.11.0'></a>
## 0.11.0 — 2023-11-21

### Added

- CLI: the `--fail` option to control the app's exit code depending on skipped files (#24)


## 0.10.1 — 2023-11-18

### Added

- CLI: progress indicator (#21)

### Changed

- saving pictures from URLs is no longer a tested feature


## 0.10.0 — 2023-10-23

### Changed

- CLI: use default prog name (#11)
- TESTS: use `tox` to run tests
- switch from setup.py to pyproject.toml (#17)
- use src layout (#18)

### Added

- support for Python 3.12

### Removed

- support for Python 3.7


## 0.9.0 — 2023-04-04

### Added

- Library API: the `fill_area` parameter to `PictureShow.save_pdf` and `pictures_to_pdf` (#9)
- CLI: the `--fill-area` option (#9)

### Changed

- CLI: when invoked without command-line arguments, the message `Try 'pictureshow --help' for more information.` is now displayed (#7)


## 0.8.2 — 2023-03-23

### Changed

- CI/CD: build both *sdist* and *wheel*
- TESTS: switch from `PyPDF2` to `pypdf`


## 0.8.1 — 2022-05-05

### Changed

- Library API: the `pdf_file` parameter of `PictureShow.save_pdf` and `pictures_to_pdf` renamed to `output_file` (#4)
- TESTS: tests run concurrently using the [pytest-xdist](https://github.com/pytest-dev/pytest-xdist) plugin

### Added

- CI/CD: code checked for security using [bandit](https://bandit.readthedocs.io/en/latest/)


## 0.7.1 — 2022-04-29

### Changed

- CLI:
  - concise usage message
  - options sorted alphabetically in help message
  - available page sizes shown in help for `--page-size`


## 0.7.0 — 2022-04-27

### Changed

- CLI: the output file must now be specified with the `-o` or `--output-file` option
- CI/CD: PyPA's [action](https://github.com/pypa/gh-action-pypi-publish) to publish package to PyPI is used in GitHub Actions


## 0.6.5 — 2022-04-19

### Changed

- remove Python 3.6 from supported versions, add Python 3.10
- CLI: if the output filename has no extension specified, `.pdf` will be appended to it

### Added

- CI/CD: steps added to GitHub Actions workflow:
  - to publish package to PyPI
  - to [create GitHub release](https://github.com/softprops/action-gh-release)


## 0.6.4 — 2021-04-28

### Changed

- CLI: pictures do not have to be filesystem paths (can be e.g. URLs)


## 0.6.3 — 2021-04-26

### Changed

- Library API: `PictureShow.save_pdf` and `pictures_to_pdf` now return a named tuple of three values:
    - `num_ok`: number of successfully saved pictures
    - `errors`: list of items skipped due to error
    - `num_pages`: number of pages of the resulting PDF document
- CLI: additional info reported: number of pages of the resulting PDF document


## 0.6.1 — 2021-04-12

### Added

- TESTS: added tests for the command-line app


## 0.5.0 — 2021-03-07

### Added

- Library API: comma is now allowed as delimiter when specifying layout as a string, e.g. `'2,3'` is equivalent to `'2x3'`
- CLI: comma is allowed as delimiter when specifying layout, e.g. `2,3` is equivalent to `2x3`


## 0.4.0 — 2021-03-02

### Changed

- Library API: `pdf_file` is now a required keyword-only argument of the `pictures_to_pdf` function
  (all positional arguments are treated as input files)


## 0.3.6 — 2021-01-27

### Changed

- Library API: the `pdf_file` argument can now be specified either as a string (just like in the command line interface) or as a path-like object


## 0.3.2 — 2020-12-16

### Changed

- Library API: the `page_size` and `layout` arguments can now be specified either as a string (just like in the command line interface)
  or as a sequence of two numbers (for example, `page_size='LETTER', layout='2x3'` is equivalent to `page_size=(72 * 8.5, 72 * 11), layout=(2, 3)`)
- CLI: error message includes the name of the underlying exception's class
