|build-test| |coverage| |release| |license| |pyversions| |format| |downloads|

Save pictures to PDF from the command line or from your Python programs.


Requirements
============

- Python 3.7 or higher
- `Pillow <https://pypi.org/project/Pillow/>`__
- `reportlab <https://pypi.org/project/reportlab/>`__


Installation
============

.. code::

    pip install pictureshow


Usage
=====


As a command line tool
----------------------

.. code::

    usage: pictureshow [-h] [-p SIZE] [-L] [-m MARGIN] [-l LAYOUT] [-s] [-f]
                       [-q | -v] [-V]
                       PIC [PIC ...] PDF

    positional arguments:
      PIC                   one or more input picture file paths
      PDF                   target PDF file path

    optional arguments:
      -h, --help            show this help message and exit
      -p SIZE, --page-size SIZE
                            specify page size; default is A4
      -L, --landscape       force landscape orientation of page
      -m MARGIN, --margin MARGIN
                            set width of empty space around pictures; default is
                            72 (72 points = 1 inch)
      -l LAYOUT, --layout LAYOUT
                            specify grid layout of pictures on page, e.g. 2x3 or
                            2,3; default is 1x1
      -s, --stretch-small   scale small pictures up to fit drawing area
      -f, --force-overwrite
                            save target file even if filename exists
      -q, --quiet           suppress printing to stdout
      -v, --verbose         provide details on files skipped due to error
      -V, --version         show program's version number and exit


Example 1
~~~~~~~~~

Save single picture to PDF.

.. code::

    $ pictureshow pics/potato.jpg potato.pdf
    Saved 1 picture (1 page) to 'potato.pdf'


Example 2
~~~~~~~~~

Save multiple pictures, four pictures per page (two columns, two rows),
set page to landscape Letter-sized [#]_.

.. code::

    $ pictureshow --page-size=LETTER --landscape --layout=2x2 photos/* photos
    Saved 50 pictures (13 pages) to 'photos.pdf'

Please note that if the target filename has no extension specified,
``.pdf`` will be appended to it. This only applies for the command line tool.


Example 3
~~~~~~~~~

Save pictures from URLs, set smaller margin and stretch small pictures.

.. code::

    $ pictureshow --margin=36 --stretch-small https://<picture.1.url> https://<picture.2.url> https://<picture.3.url> pics_from_web
    Saved 3 pictures (3 pages) to 'pics_from_web.pdf'


As a Python library
-------------------

Using the ``PictureShow`` class:

.. code-block:: python

    from pictureshow import PictureShow

    pic_show = PictureShow('pics/cucumber.jpg', 'pics/onion.jpg')
    pic_show.save_pdf('vegetables.pdf')


Using the ``pictures_to_pdf`` shortcut function:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    pictures_to_pdf('pics/cucumber.jpg', 'pics/onion.jpg', pdf_file='vegetables.pdf')

Please note that contrary to the ``PictureShow.save_pdf`` method, ``pdf_file``
must be specified as a keyword argument in the above example, because the
``pictures_to_pdf`` function treats all positional arguments as input files.

Another example, demonstrating all available keyword-only arguments:

.. code-block:: python

    from pathlib import Path

    from pictureshow import pictures_to_pdf

    list_of_pictures = Path.cwd().glob('pics/*')
    pictures_to_pdf(
        *list_of_pictures,
        pdf_file='pictures.pdf',
        page_size='A5',
        landscape=True,
        margin=18,
        layout=(3, 2),
        stretch_small=True,
        force_overwrite=True
    )


Footnotes
=========

.. [#] Available page sizes are:
    A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10,
    B0, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10,
    C0, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10,
    LETTER, LEGAL, ELEVENSEVENTEEN,
    JUNIOR_LEGAL, HALF_LETTER, GOV_LETTER, GOV_LEGAL, TABLOID, LEDGER

.. |build-test| image:: https://github.com/mportesdev/pictureshow/actions/workflows/build-test.yml/badge.svg
    :target: https://github.com/mportesdev/pictureshow/actions
.. |coverage| image:: https://img.shields.io/codecov/c/gh/mportesdev/pictureshow
    :target: https://codecov.io/gh/mportesdev/pictureshow
.. |release| image:: https://img.shields.io/github/v/release/mportesdev/pictureshow
    :target: https://github.com/mportesdev/pictureshow/releases/latest
.. |license| image:: https://img.shields.io/github/license/mportesdev/pictureshow
    :target: https://github.com/mportesdev/pictureshow/blob/master/LICENSE
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/pictureshow
    :target: https://pypi.org/project/pictureshow
.. |format| image:: https://img.shields.io/pypi/format/pictureshow
    :target: https://pypi.org/project/pictureshow/#files
.. |downloads| image:: https://pepy.tech/badge/pictureshow
    :target: https://pepy.tech/project/pictureshow
