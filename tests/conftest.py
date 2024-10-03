import pytest


@pytest.fixture
def new_pdf(tmp_path):
    return tmp_path / 'pictures.pdf'


@pytest.fixture
def existing_pdf(tmp_path):
    path = tmp_path / 'pictures.pdf'
    path.write_bytes(b'%PDF')
    return path


@pytest.fixture
def error_log_mock(tmp_path, mocker):
    path = tmp_path / 'test.log'
    mocker.patch('pictureshow.cli.ERROR_LOG', path)
    return path
