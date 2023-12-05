import pytest


@pytest.fixture
def new_pdf(tmp_path):
    return tmp_path / 'pictures.pdf'


@pytest.fixture
def existing_pdf(tmp_path):
    pdf_path = tmp_path / 'pictures.pdf'
    pdf_path.write_bytes(b'foo')
    return pdf_path


@pytest.fixture
def error_log(tmp_path, mocker):
    path = tmp_path / 'test.log'
    mocker.patch('pictureshow.cli.ERROR_LOG', path)
    return path
