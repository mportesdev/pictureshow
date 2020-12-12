import argparse
import os

import pictureshow


def get_args(parser):
    parser.add_argument('PIC', nargs='+',
                        help='one or more input picture file paths')
    parser.add_argument('PDF', help='output PDF file path')
    parser.add_argument('-v', '--version', action='version')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='suppress printing to stdout')
    parser.add_argument('-f', '--force-overwrite', action='store_true',
                        help='save output file even if filename exists')
    parser.add_argument('-L', '--landscape', action='store_true',
                        help='force landscape orientation of page')
    parser.add_argument('-m', '--margin', type=float, default=72,
                        help='width of empty margin on page;'
                             ' default is 72 points (1 inch)')
    parser.add_argument('-l', '--layout', default='1x1',
                        help='grid layout of pictures on page; default is 1x1')
    parser.add_argument('-s', '--stretch-small', action='store_true',
                        help='scale small pictures up to fit drawing area')

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
    parser = argparse.ArgumentParser(
        prog='pictureshow',
        description='Save pictures to PDF',
        epilog='https://pypi.org/project/pictureshow/'
    )
    parser.version = pictureshow.__version__
    args = get_args(parser)

    picture_paths = [os.path.abspath(pic_file) for pic_file in args.PIC]
    pdf_path = os.path.abspath(args.PDF)
    layout = tuple(int(s) for s in args.layout.split('x'))

    try:
        num_ok, num_errors = pictureshow.pictures_to_pdf(
            *picture_paths, pdf_file=pdf_path, landscape=args.landscape,
            margin=args.margin, layout=layout, stretch_small=args.stretch_small,
            force_overwrite=args.force_overwrite
        )
    except Exception as err:
        parser.error(err)
    else:
        if not args.quiet:
            report_results(num_ok, num_errors, pdf_path)
