Save pictures to PDF either from a command line, or in your Python programs.

As a command line tool
----------------------

Usage:

.. code::

    $ python -m pictureshow -h
    usage: pictureshow [-h] -i PICTURE -o PDF

    optional arguments:
      -h, --help            show this help message and exit
      -i PICTURE, --input PICTURE, --picture PICTURE
                            input file path
      -o PDF, --output PDF, --pdf PDF
                            output file path

Example:

.. code::

    $ python -m pictureshow --picture picture.png --pdf output_file.pdf
    Saved to file: /.../output_file.pdf

.. code::

    $ python -m pictureshow -i picture.png -o output_file.pdf
    Saved to file: /.../output_file.pdf


As a Python library
-------------------

Using the ``PictureShow`` class:

.. code-block:: python

    from pictureshow import PictureShow

    ps = PictureShow('picture.jpg')
    ps.save_pdf('output_file.pdf')

Using the ``picture_to_pdf`` shortcut function:

.. code-block:: python

    from pictureshow import picture_to_pdf

    picture_to_pdf('picture.png', 'output_file.pdf')
