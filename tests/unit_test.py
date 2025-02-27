import os
from unittest.mock import create_autospec

import pytest
from PIL import UnidentifiedImageError as ImageError

from pictureshow.backends import ImageReader
from pictureshow.core import _Box, PictureShow
from pictureshow.exceptions import (
    LayoutError, MarginError, PageSizeError, RGBColorError
)

from . import A4_WIDTH, A4_LENGTH

A4 = A4_WIDTH, A4_LENGTH
A4_LANDSCAPE = A4_LENGTH, A4_WIDTH

DEFAULTS = dict(
    force_overwrite=False,
    page_size=A4,
    landscape=False,
    bg_color=None,
    layout=(1, 1),
    margin=72,
    stretch_small=False,
    fill_cell=False,
)


def picture():
    """Return a mock to replace ImageReader objects in tests."""
    image_reader = create_autospec(ImageReader, instance=True)
    image_reader.getSize.return_value = (640, 400)

    return image_reader


class TestIterSave:
    """Test core.PictureShow._iter_save"""

    @pytest.mark.parametrize(
        'reader_side_effects, expected_ok, expected_errors',
        (
            pytest.param([picture()], 1, 0, id='1 valid'),
            pytest.param([picture(), picture()], 2, 0, id='2 valid'),
            pytest.param([picture(), ImageError()], 1, 1, id='1 valid + 1 invalid'),
        ),
    )
    def test_valid_input(
            self,
            mocker,
            reader_side_effects,
            expected_ok,
            expected_errors,
    ):
        pic_files = ['foo.png'] * len(reader_side_effects)
        output_file = 'foo.pdf'
        mocker.patch(
            'pictureshow.backends.ImageReader',
            autospec=True,
            side_effect=reader_side_effects,
        )
        mocker.patch('pictureshow.backends.Canvas', autospec=True)

        pic_show = PictureShow(*pic_files)
        list(pic_show._iter_save(output_file, **DEFAULTS))  # exhaust the generator
        result = pic_show.result

        assert result.num_ok == expected_ok
        assert len(result.errors) == expected_errors
        assert result.num_pages == expected_ok

    @pytest.mark.parametrize(
        'reader_side_effects, expected_errors',
        (
            pytest.param([ImageError()], 1, id='1 invalid'),
            pytest.param([ImageError(), ImageError()], 2, id='2 invalid'),
            pytest.param(
                [IsADirectoryError(), FileNotFoundError()], 2, id='dir + missing'
            ),
        ),
    )
    def test_invalid_input(self, mocker, reader_side_effects, expected_errors):
        pic_files = ['foo.png'] * len(reader_side_effects)
        output_file = 'foo.pdf'
        mocker.patch(
            'pictureshow.backends.ImageReader',
            autospec=True,
            side_effect=reader_side_effects,
        )
        mocker.patch('pictureshow.backends.Canvas', autospec=True)

        pic_show = PictureShow(*pic_files)
        list(pic_show._iter_save(output_file, **DEFAULTS))  # exhaust the generator
        result = pic_show.result

        assert result.num_ok == 0
        assert len(result.errors) == expected_errors
        assert result.num_pages == 0

    @pytest.mark.parametrize(
        'reader_side_effects, expected_ok, expected_pages',
        (
            pytest.param([picture(), picture()], 2, 1, id='2 valid'),
            pytest.param([picture(), picture(), picture()], 3, 2, id='3 valid'),
        ),
    )
    def test_multipage_layout(
            self,
            mocker,
            reader_side_effects,
            expected_ok,
            expected_pages,
    ):
        pic_files = ['foo.png'] * len(reader_side_effects)
        output_file = 'foo.pdf'
        mocker.patch(
            'pictureshow.backends.ImageReader',
            autospec=True,
            side_effect=reader_side_effects,
        )
        mocker.patch('pictureshow.backends.Canvas', autospec=True)
        params = {**DEFAULTS, 'layout': (1, 2)}

        pic_show = PictureShow(*pic_files)
        list(pic_show._iter_save(output_file, **params))  # exhaust the generator
        result = pic_show.result

        assert result.num_ok == expected_ok
        assert len(result.errors) == 0
        assert result.num_pages == expected_pages


class TestValidateTargetPath:
    """Test core.PictureShow._validate_target_path"""

    def test_new_file(self, new_pdf):
        result = PictureShow()._validate_target_path(new_pdf, force_overwrite=False)
        assert result == new_pdf

    def test_existing_file_raises_error(self, existing_pdf):
        with pytest.raises(FileExistsError, match="file '.*' exists"):
            PictureShow()._validate_target_path(existing_pdf, force_overwrite=False)

    def test_force_overwrite(self, existing_pdf):
        result = PictureShow()._validate_target_path(existing_pdf, force_overwrite=True)
        assert result == existing_pdf

    def test_str_converted_to_pathlike(self, new_pdf):
        result = PictureShow()._validate_target_path(
            os.fspath(new_pdf), force_overwrite=False
        )
        assert result == new_pdf


class TestValidatePageSize:
    """Test core.PictureShow._validate_page_size"""

    @pytest.mark.parametrize(
        'page_size',
        (
            pytest.param(A4, id='A4'),
            pytest.param((11.5 * 72, 8.5 * 72), id='custom'),
        ),
    )
    def test_tuple(self, page_size):
        result = PictureShow()._validate_page_size(page_size, landscape=False)
        assert result == page_size

    @pytest.mark.parametrize(
        'page_size, expected',
        (
            pytest.param('A4', A4, id="'A4'"),
            pytest.param('letter', (72 * 8.5, 72 * 11), id="'letter'"),
        ),
    )
    def test_str(self, page_size, expected):
        result = PictureShow()._validate_page_size(page_size, landscape=False)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        'page_size, expected_mm',
        (
            pytest.param('A4', [210, 297], id="'A4'"),
            pytest.param('b0', [1000, 1414], id="'b0'"),
        ),
    )
    def test_valid_name_mm(self, page_size, expected_mm):
        w, h = PictureShow()._validate_page_size(page_size, landscape=False)
        assert [n / 72 * 25.4 for n in (w, h)] == pytest.approx(expected_mm)

    @pytest.mark.parametrize(
        'page_size, expected_inches',
        (
            pytest.param('LETTER', [8.5, 11], id="'LETTER'"),
            pytest.param('legal', [8.5, 14], id="'legal'"),
        ),
    )
    def test_valid_name_inches(self, page_size, expected_inches):
        w, h = PictureShow()._validate_page_size(page_size, landscape=False)
        assert [n / 72 for n in (w, h)] == pytest.approx(expected_inches)

    @pytest.mark.parametrize(
        'page_size, expected',
        (
            pytest.param(A4, A4_LANDSCAPE, id='A4'),
            pytest.param('A3', (420 / 25.4 * 72, 297 / 25.4 * 72), id="'A3'"),
        ),
    )
    def test_portrait_converted_to_landscape(self, page_size, expected):
        result = PictureShow()._validate_page_size(page_size, landscape=True)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        'page_size, expected',
        (
            pytest.param(A4_LANDSCAPE, A4_LANDSCAPE, id='A4_LANDSCAPE'),
            pytest.param('LEDGER', [17 * 72, 11 * 72], id="'LEDGER'"),
        ),
    )
    def test_landscape_unchanged(self, page_size, expected):
        result = PictureShow()._validate_page_size(page_size, landscape=True)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        'page_size',
        (
            pytest.param((100,), id='invalid length'),
            pytest.param((500.0, 0), id='invalid value'),
        ),
    )
    def test_invalid_page_size_raises_error(self, page_size):
        with pytest.raises(
                PageSizeError, match=r'expected two positive numbers, got \(.+\)'
        ):
            PictureShow()._validate_page_size(page_size, landscape=False)

    def test_invalid_page_size_name_raises_error(self):
        with pytest.raises(
                PageSizeError,
                match="unknown page size 'A11', please use one of: ",
        ):
            PictureShow()._validate_page_size('A11', landscape=False)


class TestValidateColor:
    """Test core.PictureShow._validate_color"""

    def test_default(self):
        assert PictureShow()._validate_color(None) is None

    @pytest.mark.parametrize(
        'color, expected',
        (
            pytest.param('000000', (0, 0, 0), id='000000'),
            pytest.param('ff8c00', (255, 140, 0), id='ff8c00'),
        ),
    )
    def test_valid_color(self, color, expected):
        assert PictureShow()._validate_color(color) == expected

    @pytest.mark.parametrize(
        'color',
        (
            pytest.param('0000', id='invalid length'),
            pytest.param('bcdefg', id='invalid value'),
        ),
    )
    def test_invalid_color_raises_error(self, color):
        with pytest.raises(RGBColorError, match='6-digit hex value expected'):
            PictureShow()._validate_color(color)


class TestValidateLayout:
    """Test core.PictureShow._validate_layout"""

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param((1, 2), id='(1, 2)'),
        ),
    )
    def test_tuple(self, layout):
        assert PictureShow()._validate_layout(layout) == layout

    @pytest.mark.parametrize(
        'layout, expected',
        (
            pytest.param('1x2', (1, 2), id='1x2'),
            pytest.param('2 x 3', (2, 3), id='2 x 3'),
            pytest.param('1,2', (1, 2), id='1,2'),
            pytest.param('2, 3', (2, 3), id='2, 3'),
        ),
    )
    def test_str(self, layout, expected):
        result = PictureShow()._validate_layout(layout)
        assert result == expected

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param((1,), id='invalid length'),
            pytest.param((0, 1), id='invalid value'),
            pytest.param((1, 1.0), id='invalid type'),
        ),
    )
    def test_invalid_layout_tuple_raises_error(self, layout):
        with pytest.raises(
                LayoutError, match=r'expected two positive integers, got \(.+\)'
        ):
            PictureShow()._validate_layout(layout)

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param('1x', id='invalid format'),
            pytest.param('0x1', id='invalid value'),
        ),
    )
    def test_invalid_layout_str_raises_error(self, layout):
        with pytest.raises(
                LayoutError, match="expected two positive integers, got '.+'"
        ):
            PictureShow()._validate_layout(layout)


class TestValidPictures:
    """Test core.PictureShow._valid_pictures"""

    @pytest.mark.parametrize(
        'reader_side_effects',
        (
            pytest.param([picture()], id='1 valid'),
            pytest.param([picture(), picture()], id='2 valid'),
        ),
    )
    def test_all_valid_pictures(self, mocker, reader_side_effects):
        pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*pic_files)
        mocker.patch(
            'pictureshow.backends.ImageReader',
            autospec=True,
            side_effect=reader_side_effects,
        )
        result = list(pic_show._valid_pictures())

        assert result == reader_side_effects
        assert len(pic_show.errors) == 0

    @pytest.mark.parametrize(
        'reader_side_effects, expected',
        (
            pytest.param([1, ImageError(), 2], [1, None, 2], id='2 valid + 1 invalid'),
            pytest.param(
                [ImageError(), 1, ImageError()],
                [None, 1, None],
                id='2 invalid + 1 valid',
            ),
        ),
    )
    def test_valid_and_invalid_pictures(self, mocker, reader_side_effects, expected):
        pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*pic_files)
        mocker.patch(
            'pictureshow.backends.ImageReader',
            autospec=True,
            side_effect=reader_side_effects,
        )
        result = list(pic_show._valid_pictures())

        assert result == expected
        assert len(pic_show.errors) == expected.count(None)

    @pytest.mark.parametrize(
        'reader_side_effects, expected',
        (
            pytest.param([ImageError()], [None], id='1 invalid'),
            pytest.param([ImageError(), ImageError()], [None, None], id='2 invalid'),
            pytest.param(
                [IsADirectoryError(), FileNotFoundError()],
                [None, None],
                id='dir + missing',
            ),
        ),
    )
    def test_all_invalid_pictures(self, mocker, reader_side_effects, expected):
        pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*pic_files)
        mocker.patch(
            'pictureshow.backends.ImageReader',
            autospec=True,
            side_effect=reader_side_effects,
        )
        result = list(pic_show._valid_pictures())

        assert result == expected
        assert len(pic_show.errors) == expected.count(None)


DEFAULT_CELL = _Box(72, 72, A4_WIDTH - 144, A4_LENGTH - 144)
DEFAULT_CELL_LANDSCAPE = _Box(72, 72, A4_LENGTH - 144, A4_WIDTH - 144)


class TestPictureBox:
    """Test core.PictureShow._picture_box"""

    @pytest.mark.parametrize(
        'cell',
        (
            pytest.param(DEFAULT_CELL, id='portrait'),
            pytest.param(DEFAULT_CELL_LANDSCAPE, id='landscape'),
        ),
    )
    def test_big_wide_picture_fills_cell_x(self, cell):
        pic_width, pic_height = 800, 387
        pic_box = PictureShow()._picture_box(
            (pic_width, pic_height), cell, stretch_small=False, fill_cell=False
        )
        assert pic_box.x == 72
        assert pic_box.width == cell.width
        assert pic_box.width / pic_box.height == pytest.approx(pic_width / pic_height)

    @pytest.mark.parametrize(
        'cell',
        (
            pytest.param(DEFAULT_CELL, id='portrait'),
            pytest.param(DEFAULT_CELL_LANDSCAPE, id='landscape'),
        ),
    )
    def test_big_tall_picture_fills_cell_y(self, cell):
        pic_width, pic_height = 400, 3260
        pic_box = PictureShow()._picture_box(
            (pic_width, pic_height), cell, stretch_small=False, fill_cell=False
        )
        assert pic_box.y == 72
        assert pic_box.height == cell.height
        assert pic_box.width / pic_box.height == pytest.approx(pic_width / pic_height)

    def test_small_picture_not_resized(self):
        pic_size = 320, 200
        pic_box = PictureShow()._picture_box(
            pic_size, DEFAULT_CELL, stretch_small=False, fill_cell=False
        )
        assert pic_box.size == pic_size

    @pytest.mark.parametrize(
        'cell',
        (
            pytest.param(DEFAULT_CELL, id='portrait'),
            pytest.param(DEFAULT_CELL_LANDSCAPE, id='landscape'),
        ),
    )
    def test_small_wide_picture_stretch_small(self, cell):
        pic_width, pic_height = 192, 108
        pic_box = PictureShow()._picture_box(
            (pic_width, pic_height), cell, stretch_small=True, fill_cell=False
        )
        assert pic_box.x == 72
        assert pic_box.width == cell.width
        assert pic_box.width / pic_box.height == pytest.approx(pic_width / pic_height)

    @pytest.mark.parametrize(
        'cell',
        (
            pytest.param(DEFAULT_CELL, id='portrait'),
            pytest.param(DEFAULT_CELL_LANDSCAPE, id='landscape'),
        ),
    )
    def test_small_tall_picture_stretch_small(self, cell):
        pic_width, pic_height = 68, 112
        pic_box = PictureShow()._picture_box(
            (pic_width, pic_height), cell, stretch_small=True, fill_cell=False
        )
        assert pic_box.y == 72
        assert pic_box.height == cell.height
        assert pic_box.width / pic_box.height == pytest.approx(pic_width / pic_height)

    @pytest.mark.parametrize(
        'pic_size',
        (
            pytest.param((800, 387), id='big wide picture'),
            pytest.param((400, 3260), id='big tall picture'),
            pytest.param((320, 200), id='small picture'),
        ),
    )
    def test_fill_cell(self, pic_size):
        cell = DEFAULT_CELL
        pic_box = PictureShow()._picture_box(
            pic_size, cell, stretch_small=False, fill_cell=True
        )
        assert pic_box.position == (72, 72)
        assert pic_box.size == cell.size


class TestCells:
    """Test core.PictureShow._cells"""

    @pytest.mark.parametrize(
        'num_rows',
        (
            pytest.param(2, id='1x2'),
            pytest.param(3, id='1x3'),
        ),
    )
    def test_single_column_layout(self, num_rows):
        margin = 72
        cells = list(PictureShow()._cells((1, num_rows), A4, margin))

        assert len(cells) == num_rows
        assert cells[0].x == pytest.approx(margin)
        assert cells[0].width == pytest.approx(A4_WIDTH - 2 * margin)
        assert cells[-1].position == pytest.approx((margin, margin))

    @pytest.mark.parametrize(
        'num_cols',
        (
            pytest.param(2, id='2x1'),
            pytest.param(3, id='3x1'),
        ),
    )
    def test_single_row_layout(self, num_cols):
        margin = 72
        cells = list(PictureShow()._cells((num_cols, 1), A4, margin))

        assert len(cells) == num_cols
        assert cells[0].position == pytest.approx((margin, margin))
        assert cells[0].height == pytest.approx(A4_LENGTH - 2 * margin)

    def test_3x3_layout(self):
        margin = 72
        cells = list(PictureShow()._cells((3, 3), A4, margin))

        assert len(cells) == 9
        assert cells[0].x == pytest.approx(margin)
        assert cells[6].position == pytest.approx((margin, margin))
        assert cells[8].y == pytest.approx(margin)

    @pytest.mark.parametrize(
        'layout, margin',
        (
            pytest.param((1, 1), 300, id='1x1, 300'),
            pytest.param((1, 2), 285, id='1x2, 285'),
        ),
    )
    def test_high_margin_raises_error(self, layout, margin):
        with pytest.raises(MarginError, match='margin value too high: .+'):
            list(PictureShow()._cells(layout, A4, margin))
