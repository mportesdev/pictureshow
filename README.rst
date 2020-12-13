Save pictures to PDF — from the command line, or from your Python programs.

As a command line tool
----------------------

Usage:

.. code::

    usage: pictureshow [-h] [-v] [-q] [-f] [-L] [-m MARGIN] [-l LAYOUT] [-s]
                       PIC [PIC ...] PDF

    positional arguments:
      PIC                   one or more input picture file paths
      PDF                   output PDF file path

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -q, --quiet           suppress printing to stdout
      -f, --force-overwrite
                            save output file even if filename exists
      -L, --landscape       force landscape orientation of page
      -m MARGIN, --margin MARGIN
                            width of empty margin on page; default is 72 points (1
                            inch)
      -l LAYOUT, --layout LAYOUT
                            grid layout of pictures on page; default is 1x1
      -s, --stretch-small   scale small pictures up to fit drawing area

Simple example — saving a single picture to PDF:

.. code::

    $ pictureshow picture.png pic.pdf
    Saved 1 picture to '/.../pic.pdf'

Using a glob pattern, in the quiet mode:

.. code::

    $ pictureshow -q *.jpg jpg_pics.pdf

Using multiple glob patterns, with half-inch margin and 1x3 pictures per page:

.. code::

    $ pictureshow --margin=36 --layout=1x3 *.png *.jpg *.gif all_pics.pdf
    Saved 32 pictures to '/.../all_pics.pdf'

Combining glob pattern and additional filenames, overwriting existing output file, stretching small pictures to page, with zero margin:

.. code::

    $ pictureshow chart.gif *.jpg figure.png pics.pdf -fsm0
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

The example above will work as long as the output file is passed as the last positional argument. It is however recommended to always use a keyword argument:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    list_of_pictures = ['pic1.png', 'pic2.jpg', 'pic3.gif']
    pictures_to_pdf(*list_of_pictures, pdf_file='pictures.pdf')

Another example, with landscape page orientation, half-inch margin and 2x2 pictures per page, stretching small pictures to area, overwriting target file if it exists:

.. code-block:: python

    from pathlib import Path

    from pictureshow import pictures_to_pdf

    list_of_pictures = sorted(Path.cwd().glob('screenshots/*.png'))
    pictures_to_pdf(
        *list_of_pictures,
        pdf_file='screenshots.pdf',
        landscape=True,
        margin=36,
        layout=(2, 2),
        stretch_small=True,
        force_overwrite=True
    )
