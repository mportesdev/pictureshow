import argparse
import os

from pictureshow.core import pictures_to_pdf


def get_args():
    parser = argparse.ArgumentParser(
        prog='pictureshow',
        description='Save pictures to PDF',
        epilog='https://pypi.org/project/pictureshow/'
    )

    parser.add_argument('PIC', nargs='+',
                        help='one or more input picture file paths')
    parser.add_argument('PDF', help='output PDF file path')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='disable printing to stdout')

    return parser.parse_args()


def report_results(num_ok, num_errors, target_path):
    if num_errors:
        print(f'{num_errors} file{"s" if num_errors > 1 else ""} skipped'
              ' because of error.')
    if num_ok != 0:
        print(f'Saved {num_ok} picture{"s" if num_ok > 1 else ""}'
              f' to {target_path!r}')
    else:
        print('No PDF file generated.')


def main():
    args = get_args()

    picture_paths = [os.path.abspath(pic_file) for pic_file in args.PIC]
    pdf_path = os.path.abspath(args.PDF)

    num_ok, num_errors = pictures_to_pdf(*picture_paths, pdf_file=pdf_path)
    if not args.quiet:
        report_results(num_ok, num_errors, pdf_path)
