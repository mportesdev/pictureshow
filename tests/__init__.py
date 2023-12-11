from pathlib import Path

from pypdf import PdfReader

TEST_FILES = Path(__file__).parent / 'files'

PIC_FILE = TEST_FILES / 'mandelbrot.png'
BAD_FILE = TEST_FILES / 'not_jpg.jpg'

PICS_1_GOOD = (PIC_FILE,)
PICS_2_GOOD = (PIC_FILE, TEST_FILES / 'plots' / 'gauss_2x2.png')
PICS_1_GOOD_1_BAD = (PIC_FILE, BAD_FILE)
PICS_1_BAD = (BAD_FILE,)
PICS_2_BAD = (BAD_FILE, TEST_FILES / 'empty.pdf')
PICS_DIR = (TEST_FILES / 'plots',)
PICS_MISSING = (TEST_FILES / 'missing.png',)

A4_WIDTH = 72 * 210 / 25.4
A4_LENGTH = 72 * 297 / 25.4
LETTER_WIDTH = 72 * 8.5
LETTER_LENGTH = 72 * 11


def assert_pdf(path, num_pages):
    assert path.exists()
    assert path.stat().st_size > 0
    assert len(PdfReader(path).pages) == num_pages


def pdf_pages(pdf_path):
    yield from PdfReader(pdf_path).pages
