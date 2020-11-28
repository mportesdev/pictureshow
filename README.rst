Save pictures to PDF — from the command line, or from your Python programs.

As a command line tool
----------------------

Usage:

.. code::

    usage: pictureshow [-h] [-v] [-q] [-m MARGIN] [-s] PIC [PIC ...] PDF

    positional arguments:
      PIC                   one or more input picture file paths
      PDF                   output PDF file path

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -q, --quiet           suppress printing to stdout
      -m MARGIN, --margin MARGIN
                            width of empty margin on page; default 72 points (1
                            inch)
      -s, --stretch-small   scale small pictures up to fit drawing area

Simple example — saving a single picture to PDF:

.. code::

    $ pictureshow picture.png pic.pdf
    Saved 1 picture to '/.../pic.pdf'

Using a glob pattern, in the quiet mode:

.. code::

    $ pictureshow -q *.jpg jpg_pics.pdf

Using multiple glob patterns, with margin width specified:

.. code::

    $ pictureshow -m 36 *.png *.jpg *.gif all_pics.pdf
    Saved 32 pictures to '/.../all_pics.pdf'

Combining glob pattern and additional filenames, with zero margin, stretching small pictures to page:

.. code::

    $ pictureshow chart.gif *.jpg graph.png pics.pdf -m 0 -s
    Saved 7 pictures to '/.../pics.pdf'

As a Python library
-------------------

Using the ``PictureShow`` class:

.. code-block:: python

    from pictureshow import PictureShow

    pic_show = PictureShow('pic1.png', 'pic2.jpg', 'pic3.gif')
    pic_show.save_pdf('pictures.pdf')

Using the ``pictures_to_pdf`` shortcut function:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    pictures_to_pdf('pic1.png', 'pic2.jpg', 'pic3.gif', 'pictures.pdf')

It is however recommended to pass the output file name as a keyword argument:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    list_of_pictures = ['pic1.png', 'pic2.jpg', 'pic3.gif']
    pictures_to_pdf(*list_of_pictures, pdf_file='pictures.pdf')

Using a glob pattern, sorted by name, with a two-inch margin, stretching smaller pictures to area:

.. code-block:: python

    from pathlib import Path

    from pictureshow import pictures_to_pdf

    list_of_pictures = sorted(Path.cwd().glob('screenshots/*.png'))
    pictures_to_pdf(
        *list_of_pictures,
        pdf_file='screenshots.pdf',
        margin=144,
        stretch_small=True
    )
