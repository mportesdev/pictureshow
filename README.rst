Save pictures to PDF either from a command line, or in your Python programs.

As a command line tool
----------------------

Usage:

.. code::

    usage: pictureshow [-h] [-v] [-q] [-m MARGIN] PIC [PIC ...] PDF

    positional arguments:
      PIC                   one or more input picture file paths
      PDF                   output PDF file path

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -q, --quiet           disable printing to stdout
      -m MARGIN, --margin MARGIN
                            width of empty margin on page; default 72 points (1
                            inch)

Examples:

.. code::

    $ pictureshow picture.png pic.pdf
    Saved 1 picture to '/.../pic.pdf'

.. code::

    $ pictureshow -q *.jpg jpg_pics.pdf

.. code::

    $ pictureshow -m 36 *.png *.jpg *.gif all_pics.pdf
    Saved 32 pictures to '/.../all_pics.pdf'

As a Python library
-------------------

Using the ``PictureShow`` class:

.. code-block:: python

    from pictureshow import PictureShow

    pic_show = PictureShow('pic1.png', 'pic2.jpg', 'pic3.gif')
    pic_show.save_pdf('pictures.pdf', margin=36)

Using the ``pictures_to_pdf`` shortcut function:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    pictures_to_pdf('pic1.png', 'pic2.jpg', 'pic3.gif', 'pictures.pdf',
                    margin=36)

It is however recommended to pass the output file name as a keyword argument:

.. code-block:: python

    from pictureshow import pictures_to_pdf

    list_of_pictures = ['pic1.png', 'pic2.jpg', 'pic3.gif']
    pictures_to_pdf(*list_of_pictures, pdf_file='pictures.pdf', margin=36)
