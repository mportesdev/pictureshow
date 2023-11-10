import argparse
import contextlib
import io
import sys
from pathlib import Path

from . import __version__
from .core import PAGE_SIZES, PictureShow


def get_args(parser):
    parser.add_argument('pictures', nargs='+', metavar='PICTURE',
                        help='one or more picture paths or URLs')
    parser.add_argument('-a', '--fill-area', action='store_true',
                        help="fill drawing area with picture, ignoring the picture's"
                             " aspect ratio")
    parser.add_argument('-f', '--force-overwrite', action='store_true',
                        help='save to output filename even if file exists')
    parser.add_argument('-L', '--landscape', action='store_true',
                        help='set landscape orientation of page; default is portrait')
    parser.add_argument('-l', '--layout', default='1x1',
                        help='specify grid layout (columns x rows) of pictures on page,'
                             ' e.g. 2x3 or 2,3; default is 1x1')
    parser.add_argument('-m', '--margin', type=float, default=72,
                        help='set width of empty space around pictures;'
                             ' default is 72 (72 points = 1 inch)')
    parser.add_argument('-o', '--output-file', required=True, metavar='PATH',
                        help='path of the output PDF file (required)')
    parser.add_argument('-p', '--page-size', default='A4', metavar='SIZE',
                        help=f'specify page size; default is A4'
                             f' (available sizes: {", ".join(PAGE_SIZES)})')
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('-q', '--quiet', action='store_true',
                                 help='suppress printing to stdout')
    parser.add_argument('-s', '--stretch-small', action='store_true',
                        help='scale small pictures up to fit drawing area')
    verbosity_group.add_argument('-v', '--verbose', action='store_true',
                                 help='show details on files skipped due to error')
    parser.add_argument('-V', '--version', action='version')

    return parser.parse_args()


def report_results(result, output_file, verbose=False):
    unique_errors = dict(result.errors)
    num_errors = len(unique_errors)
    if num_errors > 0:
        print(f'{_number(num_errors, "file")} skipped due to error.')
        if verbose:
            for pic_file, error in unique_errors.items():
                print(f'{pic_file}:\n{type(error).__name__}: {error}\n')

    if result.num_ok > 0:
        print(f'Saved {_number(result.num_ok, "picture")}'
              f' ({_number(result.num_pages, "page")}) to {output_file!r}')
    else:
        print('Nothing to save.')


def _number(number, noun):
    """Return a repr of amount in correct grammatical number."""
    suffix = 's' if number > 1 else ''
    return f'{number} {noun}{suffix}'


def _ensure_suffix(file_path):
    """If `file_path` has no suffix, add '.pdf' to it."""
    path = Path(file_path)
    if path.suffix:
        return file_path
    return str(path.with_suffix('.pdf'))


def main():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options] PICTURE [PICTURE ...] -o PATH',
        description='Save pictures to PDF.',
        epilog='https://pypi.org/project/pictureshow/'
    )
    parser.version = __version__

    # handle special case before parsing args
    if not sys.argv[1:]:
        parser.print_usage(file=sys.stderr)
        parser.exit(2, f"Try '{parser.prog} --help' for more information.\n")

    args = get_args(parser)
    output_file = _ensure_suffix(args.output_file)

    stdout_context = (
        contextlib.redirect_stdout(io.StringIO()) if args.quiet
        else contextlib.nullcontext()
    )
    with stdout_context:
        try:
            pic_show = PictureShow(*args.pictures)
            for ok_flag in pic_show._save_pdf(
                output_file=output_file,
                page_size=args.page_size,
                landscape=args.landscape,
                margin=args.margin,
                layout=args.layout,
                stretch_small=args.stretch_small,
                fill_area=args.fill_area,
                force_overwrite=args.force_overwrite
            ):
                print('.' if ok_flag else '!', end='', flush=True)
            print()
            result = pic_show.result
        except Exception as err:
            parser.error(f'{type(err).__name__}: {err}')
        else:
            report_results(result, output_file, args.verbose)
