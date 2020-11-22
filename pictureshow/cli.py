import argparse
import os

from pictureshow.core import pictures_to_pdf


def main():
    parser = argparse.ArgumentParser('pictureshow')
    parser.add_argument('-i', '--pictures', nargs='+', required=True,
                        help='input picture file path(s)', dest='picture')
    parser.add_argument('-o', '--pdf', required=True,
                        help='output PDF file path', dest='pdf')
    args = parser.parse_args()

    picture_paths = [os.path.abspath(pic_file) for pic_file in args.picture]
    pdf_path = os.path.abspath(args.pdf)

    pictures_to_pdf(*picture_paths, pdf_file=pdf_path)
    print(f'Saved to file: {pdf_path}')
