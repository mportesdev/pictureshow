from pathlib import Path
from unittest.mock import create_autospec

import pytest
from PIL import UnidentifiedImageError as ImageError

from pictureshow.backends import ImageReader
from pictureshow.core import PictureShow
from pictureshow.exceptions import LayoutError, MarginError, PageSizeError

A4_WIDTH = 72 * 210 / 25.4
A4_LENGTH = 72 * 297 / 25.4
A4 = A4_WIDTH, A4_LENGTH
A4_LANDSCAPE = A4_LENGTH, A4_WIDTH

DEFAULTS = dict(
    page_size=A4, margin=72, layout=(1, 1), stretch_small=False, fill_area=False
)


def picture():
    """Return a mock to replace ImageReader objects in tests."""
    image_reader = create_autospec(ImageReader, instance=True)
    image_reader.getSize.return_value = (640, 400)

    return image_reader


class TestSavePdf:
    """Test core.PictureShow._save_pdf"""

    @pytest.mark.parametrize(
        'reader_side_effects, expected_ok, expected_errors',
        (
            pytest.param([picture()], 1, 0, id='1 valid'),
            pytest.param([picture(), picture()], 2, 0, id='2 valid'),
            pytest.param([picture(), ImageError], 1, 1,
                         id='1 valid + 1 invalid'),
        )
    )
    def test_valid_input(self, mocker, reader_side_effects, expected_ok,
                         expected_errors):
        pic_files = ['foo.png'] * len(reader_side_effects)
        output_file = 'foo.pdf'
        mocker.patch('pictureshow.backends.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        mocker.patch('pictureshow.backends.Canvas', autospec=True)

        pic_show = PictureShow(*pic_files)
        pic_show._save_pdf(output_file, **DEFAULTS)
        result = pic_show.result

        assert result.num_ok == expected_ok
        assert len(result.errors) == expected_errors
        assert result.num_pages == expected_ok

    @pytest.mark.parametrize(
        'reader_side_effects, expected_errors',
        (
            pytest.param([ImageError], 1, id='1 invalid'),
            pytest.param([ImageError, ImageError], 2, id='2 invalid'),
            pytest.param([OSError], 1, id='dir or missing'),
        )
    )
    def test_invalid_input(self, mocker, reader_side_effects, expected_errors):
        pic_files = ['foo.png'] * len(reader_side_effects)
        output_file = 'foo.pdf'
        mocker.patch('pictureshow.backends.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        mocker.patch('pictureshow.backends.Canvas', autospec=True)

        pic_show = PictureShow(*pic_files)
        pic_show._save_pdf(output_file, **DEFAULTS)
        result = pic_show.result

        assert result.num_ok == 0
        assert len(result.errors) == expected_errors
        assert result.num_pages == 0

    @pytest.mark.parametrize(
        'reader_side_effects, expected_ok, expected_pages',
        (
            pytest.param([picture(), picture()], 2, 1, id='2 valid'),
            pytest.param([picture(), picture(), picture()], 3, 2, id='3 valid'),
        )
    )
    def test_multipage_layout(self, mocker, reader_side_effects, expected_ok,
                              expected_pages):
        pic_files = ['foo.png'] * len(reader_side_effects)
        output_file = 'foo.pdf'
        mocker.patch('pictureshow.backends.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        mocker.patch('pictureshow.backends.Canvas', autospec=True)
        params = {**DEFAULTS, 'layout': (1, 2)}

        pic_show = PictureShow(*pic_files)
        pic_show._save_pdf(output_file, **params)
        result = pic_show.result

        assert result.num_ok == expected_ok
        assert len(result.errors) == 0
        assert result.num_pages == expected_pages


class TestValidateTargetPath:
    """Test core.PictureShow._validate_target_path"""

    def test_nonexistent_target_file(self, mocker):
        Path = mocker.patch('pictureshow.core.Path', autospec=True)
        Path.return_value.exists.return_value = False
        output_file = 'foo.pdf'

        result = PictureShow()._validate_target_path(output_file,
                                                     force_overwrite=False)
        assert result == output_file

    def test_existing_target_file_raises_error(self, mocker):
        Path = mocker.patch('pictureshow.core.Path', autospec=True)
        Path.return_value.exists.return_value = True

        with pytest.raises(FileExistsError, match="file '.*' exists"):
            PictureShow()._validate_target_path('foo.pdf',
                                                force_overwrite=False)

    def test_force_overwrite_existing_file(self, mocker):
        Path = mocker.patch('pictureshow.core.Path', autospec=True)
        Path.return_value.exists.return_value = True
        output_file = 'foo.pdf'

        result = PictureShow()._validate_target_path(output_file,
                                                     force_overwrite=True)
        assert result == output_file

    def test_target_pathlike_converted_to_str(self, mocker):
        Path_mock = mocker.patch('pictureshow.core.Path', autospec=True)
        Path_mock.return_value.exists.return_value = False
        output_file = Path('foo.pdf')

        result = PictureShow()._validate_target_path(output_file,
                                                     force_overwrite=False)
        assert result == str(output_file)


class TestValidatePageSize:
    """Test core.PictureShow._validate_page_size"""

    @pytest.mark.parametrize(
        'page_size',
        (
            pytest.param(A4, id='A4'),
            pytest.param((11.5 * 72, 8.5 * 72), id='custom'),
        )
    )
    def test_page_size_as_tuple(self, page_size):
        result = PictureShow()._validate_page_size(page_size, landscape=False)
        assert result == page_size

    @pytest.mark.parametrize(
        'page_size, expected',
        (
            pytest.param('A4', A4, id="'A4'"),
            pytest.param('letter', (72 * 8.5, 72 * 11), id="'letter'"),
        )
    )
    def test_page_size_as_str(self, page_size, expected):
        result = PictureShow()._validate_page_size(page_size, landscape=False)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        'page_size, expected_mm',
        (
            pytest.param('A4', [210, 297], id="'A4'"),
            pytest.param('b0', [1000, 1414], id="'b0'"),
        )
    )
    def test_valid_names_mm(self, page_size, expected_mm):
        w, h = PictureShow()._validate_page_size(page_size, landscape=False)
        assert [n / 72 * 25.4 for n in (w, h)] == pytest.approx(expected_mm)

    @pytest.mark.parametrize(
        'page_size, expected_inches',
        (
            pytest.param('LETTER', [8.5, 11], id="'LETTER'"),
            pytest.param('legal', [8.5, 14], id="'legal'"),
        )
    )
    def test_valid_names_inches(self, page_size, expected_inches):
        w, h = PictureShow()._validate_page_size(page_size, landscape=False)
        assert [n / 72 for n in (w, h)] == pytest.approx(expected_inches)

    @pytest.mark.parametrize(
        'page_size, expected',
        (
            pytest.param(A4, A4_LANDSCAPE, id='A4'),
            pytest.param('A3', (420 / 25.4 * 72, 297 / 25.4 * 72), id="'A3'"),
            pytest.param((8.5*72, 10.5*72), (10.5*72, 8.5*72), id='custom'),
        )
    )
    def test_portrait_converted_to_landscape(self, page_size, expected):
        result = PictureShow()._validate_page_size(page_size, landscape=True)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        'page_size, expected',
        (
            pytest.param(A4_LANDSCAPE, A4_LANDSCAPE, id='A4'),
            pytest.param('LEDGER', [17 * 72, 11 * 72], id="'LEDGER'"),
            pytest.param((10.5*72, 8.5*72), (10.5*72, 8.5*72), id='custom'),
        )
    )
    def test_landscape_remains_landscape(self, page_size, expected):
        result = PictureShow()._validate_page_size(page_size, landscape=True)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        'page_size',
        (
            pytest.param((100,), id='invalid length (1)'),
            pytest.param((100, 100, 100), id='invalid length (3)'),
            pytest.param((500.0, 0), id='invalid value (zero)'),
            pytest.param((500.0, -200.0), id='invalid value (negative)'),
            pytest.param((500.0, '500.0'), id='invalid type (str)'),
            pytest.param(1, id='not iterable'),
        )
    )
    def test_invalid_page_size_raises_error(self, page_size):
        with pytest.raises(PageSizeError,
                           match='two positive numbers expected'):
            PictureShow()._validate_page_size(page_size, landscape=False)

    @pytest.mark.parametrize(
        'page_size',
        (
            pytest.param('A11', id="'A11'"),
            pytest.param('portrait', id="'portrait'"),
        )
    )
    def test_invalid_page_size_name_raises_error(self, page_size):
        with pytest.raises(PageSizeError,
                           match='unknown page size .+,'
                                 ' please use one of: A0, A1.+'):
            PictureShow()._validate_page_size(page_size, landscape=False)


class TestValidateLayout:
    """Test core.PictureShow._validate_layout"""

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param((1, 1), id='(1, 1)'),
            pytest.param((1, 2), id='(1, 2)'),
            pytest.param((4, 2), id='(4, 2)'),
        )
    )
    def test_layout_as_tuple(self, layout):
        assert PictureShow()._validate_layout(layout) == layout

    @pytest.mark.parametrize(
        'layout, expected',
        (
            pytest.param([1, 2], (1, 2), id='list'),
            pytest.param(range(2, 5)[:2], (2, 3), id='iter'),
            pytest.param(b'\x05\x03', (5, 3), id='bytes'),
        )
    )
    def test_layout_as_other_sequence(self, layout, expected):
        result = PictureShow()._validate_layout(layout)
        assert result == expected

    @pytest.mark.parametrize(
        'layout, expected',
        (
            pytest.param('1x1', (1, 1), id='1x1'),
            pytest.param('02x03', (2, 3), id='02x03'),
            pytest.param(' 3 x 1 ', (3, 1), id=' 3 x 1 '),
            pytest.param('1,1', (1, 1), id='1,1'),
            pytest.param('03,01', (3, 1), id='03,01'),
            pytest.param(' 2 , 3 ', (2, 3), id=' 2 , 3 '),
        )
    )
    def test_layout_as_str(self, layout, expected):
        result = PictureShow()._validate_layout(layout)
        assert result == expected

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param((1,), id='invalid length (1)'),
            pytest.param((1, 1, 1), id='invalid length (3)'),
            pytest.param((0, 1), id='invalid value (zero)'),
            pytest.param((-1, 3), id='invalid value (negative)'),
            pytest.param((1, 0.5), id='invalid type (float)'),
            pytest.param(('1', '1'), id='invalid type (str)'),
            pytest.param(0, id='not iterable'),
        )
    )
    def test_invalid_layout_raises_error(self, layout):
        with pytest.raises(LayoutError, match='two positive integers expected'):
            PictureShow()._validate_layout(layout)

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param('1', id='invalid length (1)'),
            pytest.param('1x1x1', id='invalid length (3)'),
            pytest.param('0x1', id='invalid value (zero)'),
            pytest.param('-1x3', id='invalid value (negative)'),
            pytest.param('1x0.5', id='invalid type (float)'),
        )
    )
    def test_invalid_layout_str_raises_error(self, layout):
        with pytest.raises(LayoutError, match='two positive integers expected'):
            PictureShow()._validate_layout(layout)


class TestValidPictures:
    """Test core.PictureShow._valid_pictures"""

    @pytest.mark.parametrize(
        'reader_side_effects',
        (
            pytest.param([picture()], id='1 valid'),
            pytest.param([picture(), picture()], id='2 valid'),
        )
    )
    def test_all_valid_pictures(self, mocker, reader_side_effects):
        pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*pic_files)
        mocker.patch('pictureshow.backends.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        result = list(pic_show._valid_pictures())

        assert result == reader_side_effects
        assert len(pic_show.errors) == 0

    @pytest.mark.parametrize(
        'reader_side_effects, expected',
        (
            pytest.param([1, ImageError, 2], [1, 2], id='2 valid + 1 invalid'),
            pytest.param([ImageError, 1, ImageError], [1],
                         id='2 invalid + 1 valid'),
        )
    )
    def test_valid_and_invalid_pictures(self, mocker, reader_side_effects,
                                        expected):
        pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*pic_files)
        mocker.patch('pictureshow.backends.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        result = list(pic_show._valid_pictures())

        assert result == expected
        assert len(pic_show.errors) == len(pic_files) - len(expected)

    @pytest.mark.parametrize(
        'reader_side_effects',
        (
            pytest.param([ImageError], id='1 invalid'),
            pytest.param([ImageError, ImageError], id='2 invalid'),
            pytest.param([OSError], id='dir or missing'),
        )
    )
    def test_all_invalid_pictures(self, mocker, reader_side_effects):
        pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*pic_files)
        mocker.patch('pictureshow.backends.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        result = list(pic_show._valid_pictures())

        assert result == []
        assert len(pic_show.errors) == len(pic_files)


A4_PORTRAIT_MARGIN_72 = (A4_WIDTH - 144, A4_LENGTH - 144)
A4_LANDSCAPE_MARGIN_72 = (A4_LENGTH - 144, A4_WIDTH - 144)


class TestPositionAndSize:
    """Test core.PictureShow._position_and_size"""

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((800, 387), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((800, 387), A4_LANDSCAPE_MARGIN_72, id='landscape'),
        )
    )
    def test_big_wide_picture_fills_area_x(self, pic_size, area_size):
        original_aspect = pic_size[0] / pic_size[1]
        x, y, new_width, new_height = PictureShow()._position_and_size(
            pic_size, area_size, False, False
        )
        assert x == 0
        assert new_width == area_size[0]
        assert new_width / new_height == pytest.approx(original_aspect)

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((400, 3260), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((400, 3260), A4_LANDSCAPE_MARGIN_72, id='landscape'),
        )
    )
    def test_big_tall_picture_fills_area_y(self, pic_size, area_size):
        original_aspect = pic_size[0] / pic_size[1]
        x, y, new_width, new_height = PictureShow()._position_and_size(
            pic_size, area_size, False, False
        )
        assert y == 0
        assert new_height == area_size[1]
        assert new_width / new_height == pytest.approx(original_aspect)

    def test_small_picture_not_resized(self):
        pic_size = (320, 200)
        x, y, new_width, new_height = PictureShow()._position_and_size(
            pic_size, A4_PORTRAIT_MARGIN_72, False, False
        )
        assert (new_width, new_height) == pic_size

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((192, 108), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((192, 108), A4_LANDSCAPE_MARGIN_72, id='landscape'),
        )
    )
    def test_small_wide_picture_stretch_small(self, pic_size, area_size):
        original_aspect = pic_size[0] / pic_size[1]
        x, y, new_width, new_height = PictureShow()._position_and_size(
            pic_size, area_size, stretch_small=True, fill_area=False
        )
        assert x == 0
        assert new_width == area_size[0]
        assert new_width / new_height == pytest.approx(original_aspect)

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((68, 112), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((68, 112), A4_LANDSCAPE_MARGIN_72, id='landscape'),
        )
    )
    def test_small_tall_picture_stretch_small(self, pic_size, area_size):
        original_aspect = pic_size[0] / pic_size[1]
        x, y, new_width, new_height = PictureShow()._position_and_size(
            pic_size, area_size, stretch_small=True, fill_area=False
        )
        assert y == 0
        assert new_height == area_size[1]
        assert new_width / new_height == pytest.approx(original_aspect)

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((800, 387), A4_PORTRAIT_MARGIN_72, id='big wide picture'),
            pytest.param((400, 3260), A4_PORTRAIT_MARGIN_72, id='big tall picture'),
            pytest.param((320, 200), A4_PORTRAIT_MARGIN_72, id='small picture'),
        )
    )
    def test_fill_area(self, pic_size, area_size):
        x, y, new_width, new_height = PictureShow()._position_and_size(
            pic_size, area_size, stretch_small=False, fill_area=True
        )
        assert x == 0
        assert y == 0
        assert new_width == area_size[0]
        assert new_height == area_size[1]


class TestAreas:
    """Test core.PictureShow._areas"""

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param((1, 1), id='1x1'),
            pytest.param((1, 2), id='1x2'),
            pytest.param((1, 5), id='1x5'),
        )
    )
    def test_single_column_layout(self, layout):
        page_size, margin = A4, 72
        areas = list(PictureShow()._areas(layout, page_size, margin))

        # number of areas == number of rows
        assert len(areas) == layout[1]
        assert areas[-1].y == margin

        expected_width = A4_WIDTH - 2*margin
        for area in areas:
            assert area.x == margin
            assert area.width == expected_width

    @pytest.mark.parametrize(
        'layout',
        (
            pytest.param((1, 1), id='1x1'),
            pytest.param((2, 1), id='2x1'),
            pytest.param((5, 1), id='5x1'),
        )
    )
    def test_single_row_layout(self, layout):
        page_size, margin = A4, 72
        areas = list(PictureShow()._areas(layout, page_size, margin))

        # number of areas == number of columns
        assert len(areas) == layout[0]
        assert areas[0].x == margin

        expected_height = A4_LENGTH - 2*margin
        for area in areas:
            assert area.y == margin
            assert area.height == expected_height

    @pytest.mark.parametrize(
        'layout, page_size, margin',
        (
            pytest.param((3, 3), A4, 18, id='(3, 3) portrait'),
            pytest.param((3, 3), A4, 0, id='(3, 3) portrait no margin'),
            pytest.param((3, 3), A4_LANDSCAPE, 36, id='(3, 3) landscape'),
        )
    )
    def test_3x3_layout(self, layout, page_size, margin):
        areas = list(PictureShow()._areas(layout, page_size, margin))
        assert len(areas) == 9

        # areas in the left column
        for area in areas[::3]:
            assert area.x == margin

        # areas in the bottom row
        for area in areas[6:]:
            assert area.y == margin

    @pytest.mark.parametrize(
        'layout, margin',
        (
            pytest.param((1, 1), 500, id='500'),
            pytest.param((1, 1), A4_WIDTH/2, id='A4 width/2'),
            pytest.param((1, 2), 300, id='300'),
            pytest.param((1, 2), A4_LENGTH/3, id='A4 length/3'),
        )
    )
    def test_high_margin_raises_error(self, layout, margin):
        with pytest.raises(MarginError, match='margin value too high: .+'):
            list(PictureShow()._areas(layout, A4, margin))
