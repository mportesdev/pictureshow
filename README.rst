|build-test| |coverage| |bandit| |pre-commit| |release| |pyversions| |downloads|

Save pictures to PDF from the command line or from your Python programs.


Prerequisites
=============

- Python 3.7 or higher


Installation
============

.. code::

    pip install pictureshow


Usage
=====


As a command line tool
----------------------

.. code::

    usage: pictureshow [options] PICTURE [PICTURE ...] -o PATH

    positional arguments:
      PICTURE               one or more picture paths or URLs

    options:
      -h, --help            show this help message and exit
      -a, --fill-area       fill drawing area with picture, ignoring the picture's
                            aspect ratio
      -f, --force-overwrite
                            save to output filename even if file exists
      -L, --landscape       set landscape orientation of page; default is portrait
      -l LAYOUT, --layout LAYOUT
                            specify grid layout (columns x rows) of pictures on page,
                            e.g. 2x3 or 2,3; default is 1x1
      -m MARGIN, --margin MARGIN
                            set width of empty space around pictures; default is 72
                            (72 points = 1 inch)
      -o PATH, --output-file PATH
                            path of the output PDF file (required)
      -p SIZE, --page-size SIZE
                            specify page size; default is A4 (available sizes: A0,
                            A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, B0, B1, B2, B3,
                            B4, B5, B6, B7, B8, B9, B10, C0, C1, C2, C3, C4, C5, C6,
                            C7, C8, C9, C10, LETTER, LEGAL, ELEVENSEVENTEEN,
                            JUNIOR_LEGAL, HALF_LETTER, GOV_LETTER, GOV_LEGAL,
                            TABLOID, LEDGER)
      -q, --quiet           suppress printing to stdout
      -s, --stretch-small   scale small pictures up to fit drawing area
      -v, --verbose         show details on files skipped due to error
      -V, --version         show program's version number and exit


Examples
~~~~~~~~

Save single picture to PDF:

.. code::

    $ pictureshow pics/potato.jpg -o potato.pdf
    Saved 1 picture (1 page) to 'potato.pdf'

Save multiple pictures, four pictures per page (two columns, two rows),
set page orientation to landscape:

.. code::

    $ pictureshow -l 2x2 -L vegetables/* -o vegetables
    Saved 50 pictures (13 pages) to 'vegetables.pdf'

(Please note that if the output filename has no extension specified,
``.pdf`` will be appended to it. This only applies for the command line tool.)

Save pictures from web URLs, set smaller margin and stretch small pictures:

.. code::

    $ pictureshow -m 36 -s <carrot.1.url> <carrot.2.url> -o carrots_from_web
    Saved 2 pictures (2 pages) to 'carrots_from_web.pdf'


As a Python library
-------------------


Using the ``PictureShow`` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

.. code-block:: python

    from pictureshow import PictureShow

    pictures = PictureShow('pics/cucumber.jpg', 'pics/onion.jpg')
    pictures.save_pdf('vegetables.pdf')

The keyword parameters of the ``save_pdf`` method and their default values
correspond to the above shown command line options:

.. code-block:: python

    PictureShow.save_pdf(
        output_file,
        page_size='A4',
        landscape=False,
        margin=72,
        layout=(1, 1),
        stretch_small=False,
        fill_area=False,
        force_overwrite=False
    )


Using the ``pictures_to_pdf`` shortcut function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    pictures_to_pdf('pics/cucumber.jpg', 'pics/onion.jpg', output_file='vegetables.pdf')

(Please note that contrary to the ``PictureShow.save_pdf`` method, ``output_file``
must be specified as a keyword argument in the above example, because the
``pictures_to_pdf`` function treats all positional arguments as input files.)

The keyword parameters of the ``pictures_to_pdf`` function and their
default values correspond to the above shown command line options:

.. code-block:: python

    pictures_to_pdf(
        *pic_files,
        output_file,
        page_size='A4',
        landscape=False,
        margin=72,
        layout=(1, 1),
        stretch_small=False,
        fill_area=False,
        force_overwrite=False
    )


.. |build-test| image:: https://github.com/mportesdev/pictureshow/actions/workflows/build-test.yml/badge.svg
    :target: https://github.com/mportesdev/pictureshow/actions
.. |coverage| image:: https://img.shields.io/codecov/c/gh/mportesdev/pictureshow
    :target: https://codecov.io/gh/mportesdev/pictureshow
.. |bandit| image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
    :target: https://github.com/pre-commit/pre-commit
.. |release| image:: https://img.shields.io/github/v/release/mportesdev/pictureshow
    :target: https://github.com/mportesdev/pictureshow/releases/latest
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/pictureshow
    :target: https://pypi.org/project/pictureshow
.. |downloads| image:: https://pepy.tech/badge/pictureshow
    :target: https://pepy.tech/project/pictureshow
