from pathlib import Path
import subprocess

from PyPDF2 import PdfFileReader
import pytest

A4_WIDTH = 72 * 210 / 25.4

PIC_FILE = 'pics/mandelbrot.png'
PICS_1_GOOD = (PIC_FILE,)
PICS_2_GOOD = (PIC_FILE, 'pics/blender/chain_render.jpg')
PICS_GLOB = ('pics/plots/gauss*',)
PICS_1_GOOD_1_BAD = (PIC_FILE, 'pics/not_jpg.jpg')
PICS_1_BAD = ('pics/not_jpg.jpg',)
PICS_2_BAD = ('pics/not_jpg.jpg', 'pics/empty.pdf')
PICS_DIR = ('pics',)
PICS_MISSING = ('missing.png',)


@pytest.fixture(params=['pictureshow', 'python -m pictureshow'])
def app_exec(request):
    """Executable to run in CLI tests."""
    return request.param


@pytest.fixture
def temp_pdf():
    pdf_path = Path('_test_temp_.pdf')
    yield pdf_path

    # teardown
    if pdf_path.exists():
        pdf_path.unlink()


@pytest.fixture
def temp_existing():
    pdf_path = Path('_test_temp_.pdf').resolve()
    pdf_path.write_bytes(b'foo')
    yield pdf_path

    # teardown
    if pdf_path.exists():
        pdf_path.unlink()


class TestCallsToCore:
    """Test that the command line app calls the underlying function
    correctly.
    """
    pass


class TestOutput:
    """Test stdout/stderr and return code of the command line app."""
    pass

    @pytest.mark.parametrize(
        'pic_files, num_pics',
        (
            pytest.param(PICS_1_GOOD, '1 picture', id='1 good'),
            pytest.param(PICS_2_GOOD, '2 pictures', id='2 good'),
            pytest.param(PICS_GLOB, '2 pictures', id='glob'),
        )
    )
    def test_valid_input(self, app_exec, temp_pdf, pic_files, num_pics):
        command = f'{app_exec} {" ".join(pic_files)} {temp_pdf}'
        proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert f'Saved {num_pics} to ' in std_out
        assert 'skipped' not in std_out
        assert 'Nothing' not in std_out

    def test_valid_and_invalid_input(self, app_exec, temp_pdf):
        command = f'{app_exec} {" ".join(PICS_1_GOOD_1_BAD)} {temp_pdf}'
        proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert '1 file skipped due to error.' in std_out
        assert 'Saved 1 picture to ' in std_out
        assert 'Nothing' not in std_out

    @pytest.mark.parametrize(
        'pic_files, num_invalid',
        (
            pytest.param(PICS_1_BAD, '1 file', id='1bad'),
            pytest.param(PICS_2_BAD, '2 files', id='2bad'),
            pytest.param(PICS_DIR, '1 file', id='dir'),
            pytest.param(PICS_MISSING, '1 file', id='missing'),
        )
    )
    def test_invalid_input(self, app_exec, temp_pdf, pic_files, num_invalid):
        command = f'{app_exec} {" ".join(pic_files)} {temp_pdf}'
        proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert f'{num_invalid} skipped due to error.' in std_out
        assert 'Saved' not in std_out
        assert 'Nothing to save.' in std_out

    def test_invalid_page_size_throws_error(self, app_exec, temp_pdf):
        command = f'{app_exec} -pA11 {PIC_FILE} {temp_pdf}'
        proc = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'error: PageSizeError:' in std_err
        assert f"unknown page size 'A11', please use one of" in std_err

    def test_high_margin_throws_error(self, app_exec, temp_pdf):
        command = f'{app_exec} -m{A4_WIDTH/2 + 1} {PIC_FILE} {temp_pdf}'
        proc = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'error: MarginError: margin value too high: ' in std_err

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param('1x3', id='1x3'),
            pytest.param('3,2', id='3,2'),
            pytest.param('1,1', id='1,1'),
        )
    )
    def test_multiple_pictures_layout(self, app_exec, temp_pdf, layout):
        command = f'{app_exec} -l{layout} {" ".join(PICS_2_GOOD*3)} {temp_pdf}'
        proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert 'Saved 6 pictures to ' in std_out

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param('1', id='invalid length'),
            pytest.param('0x1', id='invalid value'),
        )
    )
    def test_invalid_layout_throws_error(self, app_exec, temp_pdf, layout):
        command = f'{app_exec} -l{layout} {PIC_FILE} {temp_pdf}'
        proc = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert 'error: LayoutError: two positive integers expected' in std_err

    def test_existing_target_file_throws_error(self, app_exec, temp_existing):
        command = f'{app_exec} {PIC_FILE} {temp_existing}'
        proc = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
        std_err = proc.stderr.decode()

        assert proc.returncode == 2
        assert f"error: FileExistsError: file '{temp_existing}' exists" in std_err

    def test_force_overwrite_existing_file(self, app_exec, temp_existing):
        command = f'{app_exec} -f {PIC_FILE} {temp_existing}'
        proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
        std_out = proc.stdout.decode()

        assert proc.returncode == 0
        assert 'Saved 1 picture to ' in std_out


def assert_pdf(path, num_pages):
    assert path.exists()
    assert path.stat().st_size > 0
    assert PdfFileReader(str(path)).numPages == num_pages


class TestGeneratedFile:
    """Test the PDF file generated by the command line app."""

    @pytest.mark.parametrize(
        'pic_files, num_pics',
        (
            pytest.param(PICS_1_GOOD, 1, id='1 good'),
            pytest.param(PICS_2_GOOD, 2, id='2 good'),
            pytest.param(PICS_GLOB, 2, id='glob'),
        )
    )
    def test_valid_input(self, app_exec, temp_pdf, pic_files, num_pics):
        command = f'{app_exec} {" ".join(pic_files)} {temp_pdf}'
        subprocess.run(command, shell=True, stdout=subprocess.PIPE)

        assert_pdf(temp_pdf, num_pages=num_pics)

    def test_valid_and_invalid_input(self, app_exec, temp_pdf):
        command = f'{app_exec} {" ".join(PICS_1_GOOD_1_BAD)} {temp_pdf}'
        subprocess.run(command, shell=True, stdout=subprocess.PIPE)

        assert_pdf(temp_pdf, num_pages=1)

    @pytest.mark.parametrize(
        'pic_files',
        (
            pytest.param(PICS_1_BAD, id='1bad'),
            pytest.param(PICS_2_BAD, id='2bad'),
            pytest.param(PICS_DIR, id='dir'),
            pytest.param(PICS_MISSING, id='missing'),
        )
    )
    def test_invalid_input(self, app_exec, temp_pdf, pic_files):
        command = f'{app_exec} {" ".join(pic_files)} {temp_pdf}'
        subprocess.run(command, shell=True, stdout=subprocess.PIPE)

        assert not temp_pdf.exists()

    def test_invalid_page_size(self, app_exec, temp_pdf):
        command = f'{app_exec} -pA11 {PIC_FILE} {temp_pdf}'
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)

        assert not temp_pdf.exists()

    def test_high_margin(self, app_exec, temp_pdf):
        command = f'{app_exec} -m{A4_WIDTH/2 + 1} {PIC_FILE} {temp_pdf}'
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)

        assert not temp_pdf.exists()

    @pytest.mark.parametrize(
        'layout, num_pages',
        (
            pytest.param('1x3', 2, id='1x3'),
            pytest.param('3,2', 1, id='3,2'),
            pytest.param('1,1', 6, id='1,1'),
        )
    )
    def test_multiple_pictures_layout(self, app_exec, temp_pdf, layout,
                                      num_pages):
        command = f'{app_exec} -l{layout} {" ".join(PICS_2_GOOD*3)} {temp_pdf}'
        subprocess.run(command, shell=True, stdout=subprocess.PIPE)

        assert_pdf(temp_pdf, num_pages=num_pages)

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param('1', id='invalid length'),
            pytest.param('0x1', id='invalid value'),
        )
    )
    def test_invalid_layout(self, app_exec, temp_pdf, layout):
        command = f'{app_exec} -l{layout} {PIC_FILE} {temp_pdf}'
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)

        assert not temp_pdf.exists()

    def test_existing_target_file(self, app_exec, temp_existing):
        file_contents = temp_existing.read_bytes()
        command = f'{app_exec} {PIC_FILE} {temp_existing}'
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)

        # target file exists and has not changed
        assert temp_existing.exists()
        assert temp_existing.read_bytes() == file_contents

    def test_force_overwrite_existing_file(self, app_exec, temp_existing):
        file_contents = temp_existing.read_bytes()
        command = f'{app_exec} -f {PIC_FILE} {temp_existing}'
        subprocess.run(command, shell=True, stdout=subprocess.PIPE)

        # target file has been overwritten
        assert temp_existing.exists()
        assert temp_existing.read_bytes() != file_contents
