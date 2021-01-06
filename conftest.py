from pathlib import Path

import pytest


@pytest.fixture(scope='function')
def temp_pdf():
    pdf_path = Path('pictureshow_test_temp.pdf')
    yield pdf_path

    # teardown
    if pdf_path.exists():
        pdf_path.unlink()


@pytest.fixture(scope='function')
def temp_existing():
    pdf_path = Path('pictureshow_test_existing.pdf').resolve()
    pdf_path.write_bytes(b'foo')
    yield pdf_path

    # teardown
    if pdf_path.exists():
        pdf_path.unlink()
