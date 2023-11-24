import pytest


@pytest.fixture
def new_pdf(tmp_path):
    return tmp_path / 'pictures.pdf'


@pytest.fixture
def existing_pdf(tmp_path):
    pdf_path = tmp_path / 'pictures.pdf'
    pdf_path.write_bytes(b'foo')
    return pdf_path
