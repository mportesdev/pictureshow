import argparse
import contextlib
import io
import os
import sys
from pathlib import Path

from platformdirs import user_cache_path

from . import __version__
from .core import PAGE_SIZES, PictureShow

CACHE_PATH = user_cache_path('pictureshow', ensure_exists=True)
ERROR_LOG = CACHE_PATH / 'errors.log'


class _ArgParser(argparse.ArgumentParser):
    def parse_args(self, args=None, namespace=None):
        if not args and not sys.argv[1:]:
            self.print_usage(file=sys.stderr)
            self.exit(2, f"Try '{self.prog} --help' for more information.\n")
        return super().parse_args(args, namespace)


def _setup_parser():
    parser = _ArgParser(
        usage='%(prog)s [options] PICTURE [PICTURE ...] -o PATH',
        description='Save pictures to PDF.',
        epilog='https://pypi.org/project/pictureshow/',
    )
    parser.add_argument(
        'pictures',
        nargs='+',
        metavar='PICTURE',
        help='one or more input file paths',
    )
    parser.add_argument('-V', '--version', action='version', version=__version__)

    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='do not print output to stdout',
    )
    verbosity_group.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='show details of input files skipped due to error',
    )

    parser.add_argument(
        '-F',
        '--fail',
        choices=('skipped', 'no-output', 'no'),
        default='no-output',
        metavar='MODE',
        help=(
            "control the exit code: "
            "'skipped' exits with code 2 if at least one input file was skipped "
            "due to an error; "
            "'%(default)s' (default) exits with code 2 if all files were skipped "
            "and no PDF file was saved; "
            "'no' exits with code 0 even if all files were skipped"
        ),
    )

    output_group = parser.add_argument_group('output file options')
    output_group.add_argument(
        '-o',
        '--output-file',
        required=True,
        metavar='PATH',
        help='path of the output PDF file (required)',
    )
    output_group.add_argument(
        '-f',
        '--force-overwrite',
        action='store_true',
        help='save to output file path even if file exists',
    )

    page_group = parser.add_argument_group('page properties options')
    page_group.add_argument(
        '-p',
        '--page-size',
        choices=PAGE_SIZES,
        default='A4',
        metavar='SIZE',
        help='specify page size; default is %(default)s '
             f'(available sizes: {", ".join(PAGE_SIZES)})',
    )
    page_group.add_argument(
        '-L',
        '--landscape',
        action='store_true',
        help='set landscape orientation of pages',
    )
    page_group.add_argument(
        '-b',
        '--bg-color',
        metavar='COLOR',
        help='specify page background color as 6-digit hexadecimal RGB, e.g. ff8c00',
    )

    picture_group = parser.add_argument_group('picture layout options')
    picture_group.add_argument(
        '-l',
        '--layout',
        default='1x1',
        help='specify grid layout (columns x rows) of pictures on page, '
             'e.g. 2x3 or 2,3; default is %(default)s',
    )
    picture_group.add_argument(
        '-m',
        '--margin',
        type=float,
        default=72,
        help='set width of empty space around the cells containing pictures; '
             'default is %(default)s (72 points = 1 inch)',
    )
    picture_group.add_argument(
        '-s',
        '--stretch-small',
        action='store_true',
        help='scale small pictures up to fit cells',
    )
    picture_group.add_argument(
        '-c',
        '--fill-cell',
        action='store_true',
        help="fill cells with pictures, ignoring the pictures' aspect ratio",
    )

    return parser


def _report_results(result, output_file, verbose=False):
    unique_errors = dict(result.errors)
    num_errors = len(unique_errors)

    if num_errors > 0:
        print(f'{_number(num_errors, "file")} skipped due to error.')
        with ERROR_LOG.open('w', encoding='utf8') as f:
            for pic_file, error in unique_errors.items():
                text = f'{pic_file}:\n{type(error).__name__}: {error}\n'
                print(text, file=f)
                if verbose:
                    print(text)

    if result.num_ok > 0:
        print(
            f'Saved {_number(result.num_ok, "picture")} '
            f'({_number(result.num_pages, "page")}) to {output_file!r}'
        )
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
    return os.fspath(path.with_suffix('.pdf'))


def main(argv=None):
    parser = _setup_parser()
    args = parser.parse_args(argv)
    output_file = _ensure_suffix(args.output_file)

    stdout_context = (
        contextlib.redirect_stdout(io.StringIO()) if args.quiet
        else contextlib.nullcontext()
    )
    with stdout_context:
        try:
            pic_show = PictureShow(*args.pictures)
            for ok_flag in pic_show._iter_save(
                    output_file=output_file,
                    force_overwrite=args.force_overwrite,
                    page_size=args.page_size,
                    landscape=args.landscape,
                    bg_color=args.bg_color,
                    layout=args.layout,
                    margin=args.margin,
                    stretch_small=args.stretch_small,
                    fill_cell=args.fill_cell,
            ):
                print('.' if ok_flag else '!', end='', flush=True)
            print()
            result = pic_show.result
        except Exception as err:
            parser.error(f'{type(err).__name__}: {err}')
        else:
            _report_results(result, output_file, args.verbose)

    if args.fail == 'skipped':
        exit_code = 2 if result.errors else 0
    elif args.fail == 'no-output':
        exit_code = 2 if result.num_ok == 0 else 0
    else:
        exit_code = 0
    parser.exit(exit_code)
