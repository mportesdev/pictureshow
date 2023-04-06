import subprocess  # nosec: B404
from pathlib import Path

import pytest
from pypdf import PdfReader

from pictureshow.cli import _number, _ensure_suffix

A4_WIDTH = 72 * 210 / 25.4

TEST_FILES = Path(__file__).parent / 'files'

PIC_FILE = TEST_FILES / 'mandelbrot.png'
PIC_URL = 'https://avatars.githubusercontent.com/u/43098013'
BAD_FILE = TEST_FILES / 'not_jpg.jpg'

PICS_1_GOOD = (PIC_FILE,)
PICS_2_GOOD = (PIC_FILE, TEST_FILES / 'plots' / 'gauss_2x2.png')
PICS_1_URL = (PIC_URL,)
PICS_1_GOOD_1_BAD = (PIC_FILE, BAD_FILE)
PICS_1_BAD = (BAD_FILE,)
PICS_2_BAD = (BAD_FILE, TEST_FILES / 'empty.pdf')
PICS_DIR = (TEST_FILES,)
PICS_MISSING = ('missing.png',)


@pytest.fixture
def new_pdf(tmp_path):
    return tmp_path / 'pictures.pdf'


@pytest.fixture
def existing_pdf(tmp_path):
    pdf_path = tmp_path / 'pictures.pdf'
    pdf_path.write_bytes(b'foo')
    return pdf_path


@pytest.mark.parametrize(
    'number, noun, expected',
    (
            pytest.param(1, 'file', '1 file', id='1 file'),
            pytest.param(2, 'file', '2 files', id='2 files'),
            pytest.param(1, 'picture', '1 picture', id='1 picture'),
            pytest.param(3, 'page', '3 pages', id='3 pages'),
    )
)
def test_number(number, noun, expected):
    assert _number(number, noun) == expected


@pytest.mark.parametrize(
    'path, expected',
    (
            pytest.param('pics', 'pics.pdf', id='no suffix'),
            pytest.param('pics.pdf', 'pics.pdf', id='.pdf suffix'),
            pytest.param('pics.pics', 'pics.pics', id='other suffix'),
    )
)
def test_ensure_suffix(path, expected):
    assert _ensure_suffix(path) == expected


def assert_pdf(path, num_pages):
    assert path.exists()
    assert path.stat().st_size > 0
    assert len(PdfReader(path).pages) == num_pages


class TestCommandLine:
    @pytest.mark.parametrize(
        'pic_files, num_pages, pics, pages',
        (
            pytest.param(PICS_1_GOOD, 1, '1 picture', '1 page', id='1 valid'),
            pytest.param(PICS_2_GOOD, 2, '2 pictures', '2 pages', id='2 valid'),
            pytest.param(PICS_1_URL, 1, '1 picture', '1 page', id='1 valid url'),
        )
    )
    def test_valid_input(self, new_pdf, pic_files, num_pages, pics, pages):
        pic_files = ' '.join(str(path) for path in pic_files)
        command = f'pictureshow {pic_files} -o {new_pdf}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert f'Saved {pics} ({pages}) to ' in std_out
        assert 'skipped' not in std_out
        assert 'Nothing' not in std_out
        assert_pdf(new_pdf, num_pages=num_pages)

    def test_valid_and_invalid_input(self, new_pdf):
        pic_files = ' '.join(str(path) for path in PICS_1_GOOD_1_BAD)
        command = f'pictureshow {pic_files} -o {new_pdf}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert '1 file skipped due to error.' in std_out
        assert 'Saved 1 picture (1 page) to ' in std_out
        assert 'Nothing' not in std_out
        assert_pdf(new_pdf, num_pages=1)

    @pytest.mark.parametrize(
        'pic_files, num_invalid',
        (
            pytest.param(PICS_1_BAD, '1 file', id='1 invalid'),
            pytest.param(PICS_2_BAD, '2 files', id='2 invalid'),
            pytest.param(PICS_DIR, '1 file', id='dir'),
            pytest.param(PICS_MISSING, '1 file', id='missing'),
        )
    )
    def test_invalid_input(self, new_pdf, pic_files, num_invalid):
        pic_files = ' '.join(str(path) for path in pic_files)
        command = f'pictureshow {pic_files} -o {new_pdf}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert f'{num_invalid} skipped due to error.' in std_out
        assert 'Saved' not in std_out
        assert 'Nothing to save.' in std_out
        assert not new_pdf.exists()

    def test_invalid_page_size_throws_error(self, new_pdf):
        command = f'pictureshow -pA11 {PIC_FILE} -o {new_pdf}'
        proc = subprocess.run(command.split(), stderr=subprocess.PIPE)  # nosec: B603
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'usage: pictureshow [options]' in std_err
        assert 'error: PageSizeError:' in std_err
        assert "unknown page size 'A11', please use one of" in std_err
        assert not new_pdf.exists()

    def test_high_margin_throws_error(self, new_pdf):
        command = f'pictureshow -m{A4_WIDTH/2 + 1} {PIC_FILE} -o {new_pdf}'
        proc = subprocess.run(command.split(), stderr=subprocess.PIPE)  # nosec: B603
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'usage: pictureshow [options]' in std_err
        assert 'error: MarginError: margin value too high: ' in std_err
        assert not new_pdf.exists()

    @pytest.mark.parametrize(
        'layout, num_pages, pages',
        (
            pytest.param('1x3', 2, '2 pages', id='1x3'),
            pytest.param('3,2', 1, '1 page', id='3,2'),
            pytest.param('1,1', 6, '6 pages', id='1,1'),
        )
    )
    def test_multiple_pictures_layout(self, new_pdf, layout, num_pages, pages):
        # 6 pictures
        pic_files = ' '.join(str(path) for path in PICS_2_GOOD * 3)
        command = f'pictureshow -l{layout} {pic_files} -o {new_pdf}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert f'Saved 6 pictures ({pages}) to ' in std_out
        assert_pdf(new_pdf, num_pages=num_pages)

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param('1', id='invalid format'),
            pytest.param('0x1', id='invalid value'),
        )
    )
    def test_invalid_layout_throws_error(self, new_pdf, layout):
        command = f'pictureshow -l{layout} {PIC_FILE} -o {new_pdf}'
        proc = subprocess.run(command.split(), stderr=subprocess.PIPE)  # nosec: B603
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'usage: pictureshow [options]' in std_err
        assert 'error: LayoutError: two positive integers expected' in std_err
        assert not new_pdf.exists()

    def test_existing_target_file_throws_error(self, existing_pdf):
        file_contents = existing_pdf.read_bytes()
        command = f'pictureshow {PIC_FILE} -o {existing_pdf}'
        proc = subprocess.run(command.split(), stderr=subprocess.PIPE)  # nosec: B603
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'usage: pictureshow [options]' in std_err
        assert f"error: FileExistsError: file '{existing_pdf}' exists" in std_err
        # target file exists and has not changed
        assert existing_pdf.exists()
        assert existing_pdf.read_bytes() == file_contents

    def test_force_overwrite_existing_file(self, existing_pdf):
        file_contents = existing_pdf.read_bytes()
        command = f'pictureshow -f {PIC_FILE} -o {existing_pdf}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert 'Saved 1 picture (1 page) to ' in std_out
        # target file has been overwritten
        assert_pdf(existing_pdf, num_pages=1)
        assert existing_pdf.read_bytes() != file_contents

    def test_quiet_does_not_print_to_stdout(self, new_pdf):
        command = f'pictureshow -q {PIC_FILE} -o {new_pdf}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert std_out == ''

    def test_quiet_does_not_suppress_stderr(self, existing_pdf):
        command = f'pictureshow -q {PIC_FILE} -o {existing_pdf}'
        proc = subprocess.run(command.split(), stderr=subprocess.PIPE)  # nosec: B603
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'usage: pictureshow [options]' in std_err
        assert 'FileExistsError:' in std_err

    def test_verbose(self, new_pdf):
        pic_files = ' '.join(str(path) for path in PICS_1_GOOD_1_BAD)
        command = f'pictureshow -v {pic_files} -o {new_pdf}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert '1 file skipped due to error.' in std_out
        assert 'UnidentifiedImageError' in std_out

    def test_verbose_shows_only_unique_files(self, new_pdf):
        # duplicate items
        pic_files = ' '.join(str(path) for path in PICS_2_BAD * 2)
        command = f'pictureshow -v {pic_files} -o {new_pdf}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        # only unique items reported
        assert '2 files skipped due to error.' in std_out

    def test_quiet_and_verbose_are_mutually_exclusive(self, new_pdf):
        command = f'pictureshow -qv {PIC_FILE} -o {new_pdf}'
        proc = subprocess.run(command.split(), stderr=subprocess.PIPE)  # nosec: B603
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'usage: pictureshow [options]' in std_err
        assert 'error: argument -v' in std_err
        assert 'not allowed with argument -q' in std_err

    def test_special_message_if_args_missing(self):
        command = 'pictureshow'
        proc = subprocess.run(command, stderr=subprocess.PIPE)  # nosec: B603
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'usage: pictureshow [options]' in std_err
        assert "Try 'pictureshow --help' for more information." in std_err


class TestPdfSuffix:
    """Test handling of the output file's suffix."""

    def test_pdf_suffix_added_if_suffix_missing(self, new_pdf):
        without_suffix = new_pdf.with_suffix('')
        command = f'pictureshow {PIC_FILE} -o {without_suffix}'
        proc = subprocess.run(command.split(), stdout=subprocess.PIPE)  # nosec: B603
        std_out = proc.stdout.decode()

        assert not without_suffix.exists()
        assert new_pdf.exists()
        assert f"'{new_pdf}'" in std_out

    def test_file_with_suffix_not_overwritten_if_exists(self, existing_pdf):
        file_contents = existing_pdf.read_bytes()
        without_suffix = existing_pdf.with_suffix('')
        command = f'pictureshow {PIC_FILE} -o {without_suffix}'
        proc = subprocess.run(command.split(), stderr=subprocess.PIPE)  # nosec: B603
        std_err = proc.stderr.decode()

        assert not without_suffix.exists()
        assert f"error: FileExistsError: file '{existing_pdf}' exists" in std_err
        # target file has not changed
        assert existing_pdf.read_bytes() == file_contents
