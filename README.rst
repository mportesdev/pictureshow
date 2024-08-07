|build-test| |coverage| |bandit| |pre-commit| |release| |pyversions|

Save pictures to PDF from the command line or from your Python programs.


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
      -b, --bg-color COLOR  specify page background color as 6-digit hexadecimal
                            RGB, e.g. ff8c00
      -f, --force-overwrite
                            save to output filename even if file exists
      -F, --fail MODE       If set to `skipped`, fail (exit with code 2) if at
                            least one file was skipped due to an error. If set to
                            `no-output` (default), fail if all files were skipped
                            and no PDF file was created; succeed (exit with code
                            0) if at least one file was successfully saved. If set
                            to `no`, succeed even if all files were skipped.
      -L, --landscape       set landscape orientation of page; default is portrait
      -l, --layout LAYOUT   specify grid layout (columns x rows) of pictures on
                            page, e.g. 2x3 or 2,3; default is 1x1
      -m, --margin MARGIN   set width of empty space around drawing areas; default
                            is 72 (72 points = 1 inch)
      -o, --output-file PATH
                            path of the output PDF file (required)
      -p, --page-size SIZE  specify page size; default is A4 (available sizes: A0,
                            A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, B0, B1, B2,
                            B3, B4, B5, B6, B7, B8, B9, B10, C0, C1, C2, C3, C4,
                            C5, C6, C7, C8, C9, C10, LETTER, LEGAL,
                            ELEVENSEVENTEEN, JUNIOR_LEGAL, HALF_LETTER,
                            GOV_LETTER, GOV_LEGAL, TABLOID, LEDGER)
      -q, --quiet           suppress printing to stdout
      -s, --stretch-small   scale small pictures up to fit drawing areas
      -v, --verbose         show details on files skipped due to error
      -V, --version         show program's version number and exit


Examples
~~~~~~~~

Save single picture to PDF:

.. code::

    $ pictureshow pics/potato.jpg -o potato.pdf
    .
    Saved 1 picture (1 page) to 'potato.pdf'

Save multiple pictures, four pictures per page (two columns, two rows),
set page orientation to landscape:

.. code::

    $ pictureshow -l 2x2 -L vegetables/* -o vegetables
    ..................................................
    Saved 50 pictures (13 pages) to 'vegetables.pdf'

(Please note that if the output filename has no extension specified,
``.pdf`` will be appended to it. This only applies for the command line tool.)

You can also save pictures from URLs:

.. code::

    $ pictureshow https://cdn.rebrickable.com/media/thumbs/parts/elements/6136555.jpg/250x250p.jpg https://cdn.rebrickable.com/media/thumbs/parts/elements/4119478.jpg/250x250p.jpg -o carrots
    ..
    Saved 2 pictures (2 pages) to 'carrots.pdf'

But please note that this feature is not tested and depends solely on
the underlying reportlab_ backend.


As a Python library
-------------------


Using the ``pictures_to_pdf`` shortcut function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    pictures_to_pdf(
        'pics/cucumber.jpg',
        'pics/onion.jpg',
        output_file='vegetables.pdf',
    )

The customization parameters of the ``pictures_to_pdf`` function are keyword-only
and their default values correspond to the above shown command line options:

.. code-block:: python

    pictures_to_pdf(
        *pic_files,
        output_file,
        force_overwrite=False,
        page_size='A4',
        landscape=False,
        bg_color=None,
        layout=(1, 1),
        margin=72,
        stretch_small=False,
        fill_area=False,
    )


Using the ``PictureShow`` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

.. code-block:: python

    from pictureshow import PictureShow

    pictures = PictureShow(
        'pics/cucumber.jpg',
        'pics/onion.jpg',
    )
    pictures.save_pdf('vegetables.pdf')

The customization parameters of the ``save_pdf`` method are keyword-only and
their default values correspond to the above shown command line options:

.. code-block:: python

    PictureShow.save_pdf(
        output_file,
        *,
        force_overwrite=False,
        page_size='A4',
        landscape=False,
        bg_color=None,
        layout=(1, 1),
        margin=72,
        stretch_small=False,
        fill_area=False,
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
.. _reportlab: https://pypi.org/project/reportlab
