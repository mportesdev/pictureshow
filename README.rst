Save pictures to PDF either from a command line, or in your Python programs.

As a command line tool
----------------------

Usage:

.. code::

    $ pictureshow -h
    usage: pictureshow [-h] -i PICTURE [PICTURE ...] -o PDF

    optional arguments:
      -h, --help            show this help message and exit
      -i PICTURE [PICTURE ...], --pictures PICTURE [PICTURE ...]
                            input picture file path(s)
      -o PDF, --pdf PDF     output PDF file path

Example:

.. code::

    $ pictureshow -i picture.png -o pic.pdf
    Saved 1 picture to file: /.../pic.pdf

.. code::

    $ pictureshow --pictures picture1.jpg picture2.gif --pdf pics.pdf
    Saved 2 pictures to file: /.../pics.pdf


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

    pictures_to_pdf('pic1.png', 'pic2.jpg', 'pic3.gif', pdf_file='pictures.pdf')

For a single picture, it is also possible to use the ``picture_to_pdf`` shortcut function:

.. code-block:: python

    from pictureshow import picture_to_pdf

    picture_to_pdf('picture.png', 'picture.pdf')
