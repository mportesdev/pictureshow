import pytest

from pictureshow.core import pictures_to_pdf
from pictureshow.exceptions import (
    PageSizeError, LayoutError, MarginError, RGBColorError
)

from . import (
    PIC_FILE,
    PICS_1_GOOD,
    PICS_2_GOOD,
    PICS_1_GOOD_1_BAD,
    PICS_1_BAD,
    PICS_2_BAD,
    PICS_DIR,
    PICS_MISSING,
    A4_WIDTH,
    A4_LENGTH,
    LETTER_WIDTH,
    LETTER_LENGTH,
    assert_pdf,
    pdf_pages,
)


@pytest.mark.parametrize(
    'pic_files, expected',
    (
        pytest.param(PICS_1_GOOD, (1, [], 1), id='1 valid'),
        pytest.param(PICS_2_GOOD, (2, [], 2), id='2 valid'),
    )
)
def test_valid_input(new_pdf, pic_files, expected):
    result = pictures_to_pdf(*pic_files, output_file=new_pdf)

    assert result == expected
    assert_pdf(new_pdf, expected[2])


def test_valid_and_invalid_input(new_pdf):
    result = pictures_to_pdf(*PICS_1_GOOD_1_BAD, output_file=new_pdf)

    assert result.num_ok == 1
    assert len(result.errors) == 1
    assert result.num_pages == 1
    assert_pdf(new_pdf, 1)


@pytest.mark.parametrize(
    'pic_files, expected_errors',
    (
        pytest.param(PICS_1_BAD, 1, id='1 invalid'),
        pytest.param(PICS_2_BAD, 2, id='2 invalid'),
        pytest.param(PICS_DIR, 1, id='dir'),
        pytest.param(PICS_MISSING, 1, id='missing'),
    )
)
def test_invalid_input(new_pdf, pic_files, expected_errors):
    result = pictures_to_pdf(*pic_files, output_file=new_pdf)

    assert result.num_ok == 0
    assert len(result.errors) == expected_errors
    assert result.num_pages == 0
    assert not new_pdf.exists()


def test_no_input(new_pdf):
    result = pictures_to_pdf(output_file=new_pdf)

    assert result == (0, [], 0)
    assert not new_pdf.exists()


def test_existing_target_file_raises_error(existing_pdf):
    file_contents = existing_pdf.read_bytes()
    with pytest.raises(FileExistsError, match='file .* exists'):
        pictures_to_pdf(PIC_FILE, output_file=existing_pdf)

    # target file has not changed
    assert existing_pdf.read_bytes() == file_contents


def test_force_overwrite_existing_file(existing_pdf):
    file_contents = existing_pdf.read_bytes()
    result = pictures_to_pdf(PIC_FILE, output_file=existing_pdf, force_overwrite=True)

    assert result == (1, [], 1)
    assert_pdf(existing_pdf, 1)

    # target file has been overwritten
    assert existing_pdf.read_bytes() != file_contents


def test_page_size(new_pdf):
    result = pictures_to_pdf(PIC_FILE, output_file=new_pdf, page_size='LETTER')

    assert result == (1, [], 1)
    assert_pdf(new_pdf, 1)

    # page is LETTER portrait
    page = next(pdf_pages(new_pdf))
    page_box = [float(n) for n in page.mediabox]
    assert page_box == pytest.approx([0, 0, LETTER_WIDTH, LETTER_LENGTH])


def test_invalid_page_size_raises_error(new_pdf):
    with pytest.raises(
            PageSizeError, match='unknown page size .+, please use one of: A0, A1.+'
    ):
        pictures_to_pdf(PIC_FILE, output_file=new_pdf, page_size='A11')

    assert not new_pdf.exists()


def test_landscape(new_pdf):
    result = pictures_to_pdf(PIC_FILE, output_file=new_pdf, landscape=True)

    assert result == (1, [], 1)
    assert_pdf(new_pdf, 1)

    # page is A4 landscape
    page = next(pdf_pages(new_pdf))
    page_box = [float(n) for n in page.mediabox]
    assert page_box == pytest.approx([0, 0, A4_LENGTH, A4_WIDTH])


def test_bg_color(new_pdf):
    result = pictures_to_pdf(PIC_FILE, output_file=new_pdf, bg_color='8800ff')

    assert result == (1, [], 1)
    assert_pdf(new_pdf, 1)


def test_invalid_bg_color_raises_error(new_pdf):
    with pytest.raises(RGBColorError, match='6-digit hex value expected'):
        pictures_to_pdf(PIC_FILE, output_file=new_pdf, bg_color='88ff')

    assert not new_pdf.exists()


def test_layout(new_pdf):
    result = pictures_to_pdf(*PICS_2_GOOD, output_file=new_pdf, layout=(1, 2))

    assert result == (2, [], 1)
    assert_pdf(new_pdf, 1)


def test_invalid_layout_raises_error(new_pdf):
    with pytest.raises(
            LayoutError, match=r'expected two positive integers, got \(1, 0\)'
    ):
        pictures_to_pdf(PIC_FILE, output_file=new_pdf, layout=(1, 0))

    assert not new_pdf.exists()


def test_margin(new_pdf):
    result = pictures_to_pdf(PIC_FILE, output_file=new_pdf, margin=36)

    assert result == (1, [], 1)
    assert_pdf(new_pdf, 1)


def test_high_margin_raises_error(new_pdf):
    with pytest.raises(MarginError, match=r'margin value too high: \d+'):
        pictures_to_pdf(PIC_FILE, output_file=new_pdf, margin=298)

    assert not new_pdf.exists()


def test_stretch_small(new_pdf):
    result = pictures_to_pdf(PIC_FILE, output_file=new_pdf, stretch_small=True)

    assert result == (1, [], 1)
    assert_pdf(new_pdf, 1)


def test_fill_cell(new_pdf):
    result = pictures_to_pdf(PIC_FILE, output_file=new_pdf, fill_cell=True)

    assert result == (1, [], 1)
    assert_pdf(new_pdf, 1)
