import argparse
import os

from pictureshow.core import pictures_to_pdf


def main():
    parser = argparse.ArgumentParser('pictureshow')
    parser.add_argument('picture', nargs='+',
                        help='input picture file path(s)')
    parser.add_argument('pdf', help='output PDF file path')
    args = parser.parse_args()

    picture_paths = [os.path.abspath(pic_file) for pic_file in args.picture]
    pdf_path = os.path.abspath(args.pdf)

    ok, errors = pictures_to_pdf(*picture_paths, pdf_file=pdf_path)
    if errors:
        print(f'{errors} file{"s" if errors > 1 else ""} skipped'
              ' because of error.')
    if ok != 0:
        print(
            f'Saved {ok} picture{"s" if ok > 1 else ""} to PDF file: {pdf_path}'
        )
    else:
        print('No PDF file generated.')
