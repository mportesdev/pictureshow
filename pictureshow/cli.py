import argparse
import os

from pictureshow.core import pictures_to_pdf


def main():
    parser = argparse.ArgumentParser(
        prog='pictureshow',
        description='Save pictures to PDF',
        epilog='https://pypi.org/project/pictureshow/'
    )
    parser.add_argument('PIC', nargs='+',
                        help='one or more input picture file paths')
    parser.add_argument('PDF', help='output PDF file path')
    args = parser.parse_args()

    picture_paths = [os.path.abspath(pic_file) for pic_file in args.PIC]
    pdf_path = os.path.abspath(args.PDF)

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
