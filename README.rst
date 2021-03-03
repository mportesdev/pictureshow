|pytest| |pylint| |release| |license| |pyversions| |format|

Save pictures to PDF from the command line or from your Python programs.

Requirements
------------

Python 3.6 or higher is required. The only third-party dependency is `reportlab <https://pypi.org/project/reportlab/>`__.

Installation
------------

.. code::

    pip install pictureshow

As a command line tool
----------------------

Usage:

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
                            72 points (1 inch)
      -l LAYOUT, --layout LAYOUT
                            specify grid layout of pictures on page; default is
                            1x1
      -s, --stretch-small   scale small pictures up to fit drawing area
      -f, --force-overwrite
                            save target file even if filename exists
      -q, --quiet           suppress printing to stdout
      -v, --verbose         provide details on files skipped due to error
      -V, --version         show program's version number and exit

Example 1
~~~~~~~~~

Save a single picture to PDF.

.. code::

    $ pictureshow pics/mandelbrot.png mandelbrot.pdf
    Saved 1 picture to '/.../mandelbrot.pdf'

Result:

.. image:: https://raw.githubusercontent.com/mportesdev/pictureshow/master/pics/sample_pdf_mandelbrot.png


Example 2
~~~~~~~~~

Select pictures using a glob pattern [#]_, set page to landscape Letter-sized [#]_.

.. code::

    $ pictureshow pics/plots/gauss* gauss.pdf -LpLETTER
    Saved 2 pictures to '/.../gauss.pdf'

Result:

.. image:: https://raw.githubusercontent.com/mportesdev/pictureshow/master/pics/sample_pdf_gauss.png


Example 3
~~~~~~~~~

Select pictures using a glob pattern, set half-inch margin and layout of 1x3 pictures per page.

.. code::

    $ pictureshow --margin=36 --layout=1x3 pics/*alpha.png alpha_pngs.pdf
    Saved 6 pictures to '/.../alpha_pngs.pdf'

Result:

.. image:: https://raw.githubusercontent.com/mportesdev/pictureshow/master/pics/sample_pdf_alpha.png


As a Python library
-------------------

Using the ``PictureShow`` class:

.. code-block:: python

    from pictureshow import PictureShow

    pic_show = PictureShow('pics/mandelbrot.png', 'pics/mandelbrot.jpg')
    pic_show.save_pdf('pictures.pdf')

Result:

.. image:: https://raw.githubusercontent.com/mportesdev/pictureshow/master/pics/sample_pdf_pictures.png


Using the ``pictures_to_pdf`` shortcut function:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    list_of_pictures = ['pics/mandelbrot.png', 'pics/mandelbrot.jpg']
    pictures_to_pdf(*list_of_pictures, pdf_file='pictures.pdf')

Please note that unlike the command line interface, ``pdf_file`` must be specified as a keyword argument.

Another example, demonstrating all available keyword-only arguments:

.. code-block:: python

    from pathlib import Path

    from pictureshow import pictures_to_pdf

    list_of_pictures = sorted(Path.cwd().glob('pics/oldies/*/*'))
    pictures_to_pdf(
        *list_of_pictures,
        pdf_file='oldies.pdf',
        page_size='A5',
        landscape=True,
        margin=18,
        layout=(3, 3),
        stretch_small=True,
        force_overwrite=True
    )

Result:

.. image:: https://raw.githubusercontent.com/mportesdev/pictureshow/master/pics/sample_pdf_oldies.png

Changelog
~~~~~~~~~

**version 0.3.2**

The ``page_size`` and ``layout`` arguments can now be specified either by a string (just like in the command line interface) or by a sequence of two numbers. For example, ``page_size='LETTER', layout='2x3'`` is equivalent to ``page_size=(72 * 8.5, 72 * 11), layout=(2, 3)``.

**version 0.3.6**

The ``pdf_file`` argument can now be specified either by a string (just like in the command line interface) or by a path-like object.

**version 0.4.0**

``pdf_file`` is now a required keyword-only argument of the ``pictures_to_pdf`` function. All positional arguments are treated as paths to input picture files.

Footnotes
~~~~~~~~~

.. [#] Please note that glob patterns are not expanded by the Windows command line shell.
.. [#] Available page sizes are:
    A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10,
    B0, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10,
    C0, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10,
    LETTER, LEGAL, ELEVENSEVENTEEN,
    JUNIOR_LEGAL, HALF_LETTER, GOV_LETTER, GOV_LEGAL, TABLOID, LEDGER

.. |pytest| image:: https://github.com/mportesdev/pictureshow/workflows/pytest/badge.svg
    :target: https://github.com/mportesdev/pictureshow/actions
.. |pylint| image:: https://github.com/mportesdev/pictureshow/workflows/pylint/badge.svg
    :target: https://github.com/mportesdev/pictureshow/actions
.. |release| image:: https://img.shields.io/github/v/release/mportesdev/pictureshow.svg
    :target: https://github.com/mportesdev/pictureshow/releases/tag/0.4.0
.. |license| image:: https://img.shields.io/github/license/mportesdev/pictureshow.svg
    :target: https://github.com/mportesdev/pictureshow/blob/master/LICENSE
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/pictureshow
    :target: https://pypi.org/project/pictureshow
.. |format| image:: https://img.shields.io/pypi/format/pictureshow
    :target: https://pypi.org/project/pictureshow/#files
