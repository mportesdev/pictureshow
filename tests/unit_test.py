from pathlib import Path
from unittest.mock import create_autospec

import pytest
from PIL import UnidentifiedImageError as ImageError

from pictureshow.cli import _number
from pictureshow.core import PictureShow, ImageReader
from pictureshow.exceptions import PageSizeError, MarginError, LayoutError

A4_WIDTH = 72 * 210 / 25.4
A4_LENGTH = 72 * 297 / 25.4
A4 = A4_WIDTH, A4_LENGTH
A4_LANDSCAPE = A4_LENGTH, A4_WIDTH
A4_PORTRAIT_MARGIN_72 = (A4_WIDTH - 144, A4_LENGTH - 144)
A4_LANDSCAPE_MARGIN_72 = (A4_LENGTH - 144, A4_WIDTH - 144)

DEFAULTS = {
    'page_size': A4, 'margin': 72, 'layout': (1, 1), 'stretch_small': False
}


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
            pytest.param([picture(), ImageError, picture()], 2, 1,
                         id='2 valid + 1 invalid'),
            pytest.param([ImageError, picture(), ImageError], 1, 2,
                         id='2 invalid + 1 valid'),
        )
    )
    def test_valid_input_result(self, mocker, reader_side_effects,
                                expected_ok, expected_errors):
        fake_pic_files = ['foo.png'] * len(reader_side_effects)
        fake_pdf_name = 'foo.pdf'
        mocker.patch('pictureshow.core.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        mocker.patch('pictureshow.core.Canvas', autospec=True)
        num_ok, errors = PictureShow(*fake_pic_files)._save_pdf(fake_pdf_name,
                                                                **DEFAULTS)
        assert num_ok == expected_ok
        assert len(errors) == expected_errors

    @pytest.mark.parametrize(
        'reader_side_effects, num_valid',
        (
            pytest.param([picture()], 1, id='1 valid'),
            pytest.param([picture(), picture()], 2, id='2 valid'),
            pytest.param([picture(), ImageError, picture()], 2,
                         id='2 valid + 1 invalid'),
            pytest.param([ImageError, picture(), ImageError], 1,
                         id='2 invalid + 1 valid'),
        )
    )
    def test_valid_input_calls(self, mocker, reader_side_effects, num_valid):
        fake_pic_files = ['foo.png'] * len(reader_side_effects)
        fake_pdf_name = 'foo.pdf'
        mocker.patch('pictureshow.core.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        Canvas = mocker.patch('pictureshow.core.Canvas', autospec=True)
        PictureShow(*fake_pic_files)._save_pdf(fake_pdf_name, **DEFAULTS)

        Canvas.assert_called_once_with(fake_pdf_name, pagesize=A4)

        # trace method calls of mocked Canvas object
        canvas = Canvas(fake_pdf_name)
        canvas.drawImage.assert_called()
        assert canvas.drawImage.call_count == num_valid
        canvas.showPage.assert_called_with()
        assert canvas.showPage.call_count == num_valid
        canvas.save.assert_called_once_with()

    @pytest.mark.parametrize(
        'reader_side_effects, expected_errors',
        (
            pytest.param([ImageError], 1, id='1 invalid'),
            pytest.param([ImageError, ImageError], 2, id='2 invalid'),
            pytest.param([OSError], 1, id='dir'),
            pytest.param([OSError], 1, id='missing'),
        )
    )
    def test_invalid_input_result(self, mocker, reader_side_effects,
                                  expected_errors):
        fake_pic_files = ['foo.png'] * len(reader_side_effects)
        fake_pdf_name = 'foo.pdf'
        mocker.patch('pictureshow.core.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        mocker.patch('pictureshow.core.Canvas', autospec=True)
        num_ok, errors = PictureShow(*fake_pic_files)._save_pdf(fake_pdf_name,
                                                                **DEFAULTS)
        assert num_ok == 0
        assert len(errors) == expected_errors

    @pytest.mark.parametrize(
        'reader_side_effects',
        (
            pytest.param([ImageError], id='1 invalid'),
            pytest.param([ImageError, ImageError], id='2 invalid'),
            pytest.param([OSError], id='dir'),
            pytest.param([OSError], id='missing'),
        )
    )
    def test_invalid_input_calls(self, mocker, reader_side_effects):
        fake_pic_files = ['foo.png'] * len(reader_side_effects)
        fake_pdf_name = 'foo.pdf'
        mocker.patch('pictureshow.core.ImageReader', autospec=True,
                     side_effect=reader_side_effects)
        Canvas = mocker.patch('pictureshow.core.Canvas', autospec=True)
        PictureShow(*fake_pic_files)._save_pdf(fake_pdf_name, **DEFAULTS)

        Canvas.assert_called_once_with(fake_pdf_name, pagesize=A4)

        # trace method calls of mocked Canvas object
        canvas = Canvas(fake_pdf_name)
        canvas.drawImage.assert_not_called()
        canvas.showPage.assert_not_called()
        canvas.save.assert_not_called()


class TestValidateTargetPath:
    """Test core.PictureShow._validate_target_path"""

    def test_nonexistent_target_file(self, mocker):
        Path = mocker.patch('pictureshow.core.Path', autospec=True)
        Path.return_value.exists.return_value = False
        pdf_file = 'foo.pdf'

        result = PictureShow()._validate_target_path(pdf_file,
                                                     force_overwrite=False)
        assert result == pdf_file

    def test_existing_target_file_raises_error(self, mocker):
        Path = mocker.patch('pictureshow.core.Path', autospec=True)
        Path.return_value.exists.return_value = True

        with pytest.raises(FileExistsError, match="file '.*' exists"):
            PictureShow()._validate_target_path('foo.pdf',
                                                force_overwrite=False)

    def test_force_overwrite_existing_file(self, mocker):
        Path = mocker.patch('pictureshow.core.Path', autospec=True)
        Path.return_value.exists.return_value = True
        pdf_file = 'foo.pdf'

        result = PictureShow()._validate_target_path(pdf_file,
                                                     force_overwrite=True)
        assert result == pdf_file

    def test_target_path_as_pathlike(self, mocker):
        Path_mock = mocker.patch('pictureshow.core.Path', autospec=True)
        Path_mock.return_value.exists.return_value = False
        pdf_file = 'foo.pdf'

        result = PictureShow()._validate_target_path(Path(pdf_file),
                                                     force_overwrite=False)
        assert result == pdf_file


class TestValidatePageSize:
    """Test core.PictureShow._validate_page_size"""

    @pytest.mark.parametrize(
        'page_size',
        (
            pytest.param(A4, id='A4'),
            pytest.param(A4_LANDSCAPE, id='A4 landscape'),
            pytest.param((8 * 72, 11 * 72), id='(int, int)'),
            pytest.param((11.5 * 72, 8.5 * 72), id='(float, float)'),
        )
    )
    def test_page_size_as_tuple(self, page_size):
        result = PictureShow()._validate_page_size(page_size, landscape=False)
        assert result == page_size

    @pytest.mark.parametrize(
        'page_size, expected',
        (
            pytest.param('A4', A4, id="'A4'"),
            pytest.param('LETTER', (72 * 8.5, 72 * 11), id="'LETTER'"),
            pytest.param('c5', (162 / 25.4 * 72, 229 / 25.4 * 72), id="'c5'"),
        )
    )
    def test_page_size_as_str(self, page_size, expected):
        result = PictureShow()._validate_page_size(page_size, landscape=False)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        'page_size, expected_mm',
        (
            pytest.param('A4', [210, 297], id="'A4'"),
            pytest.param('A5', [148, 210], id="'A5'"),
            pytest.param('a4', [210, 297], id="'a4'"),
            pytest.param('b0', [1000, 1414], id="'b0'"),
        )
    )
    def test_valid_names_mm(self, page_size, expected_mm):
        result = PictureShow()._validate_page_size(page_size, landscape=False)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert [n / 72 * 25.4 for n in result] == pytest.approx(expected_mm)

    @pytest.mark.parametrize(
        'page_size, expected_inches',
        (
            pytest.param('LETTER', [8.5, 11], id="'LETTER'"),
            pytest.param('letter', [8.5, 11], id="'letter'"),
            pytest.param('LEGAL', [8.5, 14], id="'LEGAL'"),
            pytest.param('legal', [8.5, 14], id="'legal'"),
        )
    )
    def test_valid_names_inches(self, page_size, expected_inches):
        result = PictureShow()._validate_page_size(page_size, landscape=False)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert [n / 72 for n in result] == pytest.approx(expected_inches)

    @pytest.mark.parametrize(
        'page_size, expected',
        (
            pytest.param(A4, A4_LANDSCAPE, id='A4'),
            pytest.param((5 * 72, 8 * 72), (8 * 72, 5 * 72), id='5" x 8"'),
            pytest.param((8.5 * 72, 10.5 * 72), (10.5 * 72, 8.5 * 72),
                         id='custom'),
            pytest.param('A3', [420 / 25.4 * 72, 297 / 25.4 * 72], id="'A3'"),
            pytest.param('gov_letter', [10.5 * 72, 8 * 72], id="'gov_letter'"),
            pytest.param(A4_LANDSCAPE, A4_LANDSCAPE, id='A4 landscape'),
            pytest.param((10.5 * 72, 8.5 * 72), (10.5 * 72, 8.5 * 72),
                         id='custom landscape'),
        )
    )
    def test_convert_to_landscape(self, page_size, expected):
        result = PictureShow()._validate_page_size(page_size, landscape=True)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize(
        'page_size',
        (
            pytest.param((100,), id='invalid length (1)'),
            pytest.param((100, 100, 100), id='invalid length (3)'),
            pytest.param((500.0, 0), id='invalid value (zero)'),
            pytest.param((500.0, -200.0), id='invalid value (negative)'),
            pytest.param((500.0, '500.0'), id='invalid type (float, str)'),
            pytest.param(('200', '100'), id='invalid type (str, str)'),
            pytest.param(1, id='invalid type (int)'),
            pytest.param(1.0, id='invalid type (float)'),
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
            pytest.param('210x297', id="'210x297'"),
            pytest.param('inch', id="'inch'"),
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
            pytest.param((4, 1), id='(4, 1)'),
            pytest.param((2, 3), id='(2, 3)'),
        )
    )
    def test_layout_as_tuple(self, layout):
        assert PictureShow()._validate_layout(layout) == layout

    @pytest.mark.parametrize(
        'layout, expected',
        (
            pytest.param([2, 2], (2, 2), id='list'),
            pytest.param(b'\t\n', (9, 10), id='bytes'),
            pytest.param(iter([4, 3]), (4, 3), id='iter'),
        )
    )
    def test_layout_as_other_iterable(self, layout, expected):
        result = PictureShow()._validate_layout(layout)
        assert result == expected

    @pytest.mark.parametrize(
        'layout, expected',
        (
            pytest.param('1x1', (1, 1), id='1x1'),
            pytest.param('010x005', (10, 5), id='010x005'),
            pytest.param(' 3 x 1 ', (3, 1), id=' 3 x 1 '),
            pytest.param('1,1', (1, 1), id='1,1'),
            pytest.param('02,03', (2, 3), id='02,03'),
            pytest.param(' 2 , 2 ', (2, 2), id=' 2 , 2 '),
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
            pytest.param(('1', '1'), id='invalid type (str, str)'),
            pytest.param(('A', 'B'), id='non-numeric'),
            pytest.param(0, id='non-iterable (int)'),
            pytest.param(object(), id='non-iterable (object())'),
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
            pytest.param('AxB', id='non-numeric'),
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
            pytest.param(['1'], id='1 valid'),
            pytest.param(['1', '2'], id='2 valid'),
            pytest.param(['1', '2', '3', '4', '5'], id='5 valid'),
        )
    )
    def test_all_valid_pictures(self, mocker, reader_side_effects):
        fake_pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*fake_pic_files)
        image_reader = mocker.patch('pictureshow.core.ImageReader',
                                    autospec=True,
                                    side_effect=reader_side_effects)
        result = list(pic_show._valid_pictures())

        image_reader.assert_called_with('foo.png')
        assert image_reader.call_count == len(fake_pic_files)

        assert result == reader_side_effects
        assert len(pic_show.errors) == 0

    @pytest.mark.parametrize(
        'reader_side_effects, expected',
        (
            pytest.param(['1', ImageError, '2'], ['1', '2'],
                         id='2 valid + 1 invalid'),
            pytest.param([ImageError, '1', ImageError], ['1'],
                         id='2 invalid + 1 valid'),
        )
    )
    def test_valid_and_invalid_pictures(self, mocker, reader_side_effects,
                                        expected):
        fake_pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*fake_pic_files)
        image_reader = mocker.patch('pictureshow.core.ImageReader',
                                    autospec=True,
                                    side_effect=reader_side_effects)

        result = list(pic_show._valid_pictures())
        image_reader.assert_called_with('foo.png')
        assert image_reader.call_count == len(fake_pic_files)

        assert result == expected
        assert len(pic_show.errors) == len(fake_pic_files) - len(expected)

    @pytest.mark.parametrize(
        'reader_side_effects',
        (
            pytest.param([ImageError], id='1 invalid'),
            pytest.param([ImageError, ImageError], id='2 invalid'),
            pytest.param([OSError], id='dir'),
            pytest.param([OSError], id='missing'),
        )
    )
    def test_all_invalid_pictures(self, mocker, reader_side_effects):
        fake_pic_files = ['foo.png'] * len(reader_side_effects)
        pic_show = PictureShow(*fake_pic_files)
        image_reader = mocker.patch('pictureshow.core.ImageReader',
                                    autospec=True,
                                    side_effect=reader_side_effects)

        result = list(pic_show._valid_pictures())
        image_reader.assert_called_with('foo.png')
        assert image_reader.call_count == len(fake_pic_files)

        assert result == []
        assert len(pic_show.errors) == len(fake_pic_files)


class TestPositionAndSize:
    """Test core.PictureShow._position_and_size"""

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((800, 387), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((800, 387), A4_LANDSCAPE_MARGIN_72, id='landscape'),
            pytest.param((1000, 1500), A4_PORTRAIT_MARGIN_72, id='2:3 portrait'),
            pytest.param(
                (1500, 1000),
                A4_LANDSCAPE_MARGIN_72,
                id='3:2 landscape',
                marks=pytest.mark.xfail(
                    raises=AssertionError,
                    reason='picture is wider than page, but not wider than area'
                )
            ),
        )
    )
    def test_big_wide_picture(self, pic_size, area_size):
        aspect_ratio = pic_size[0] / pic_size[1]
        area_width, area_height = area_size
        x, y, pic_width, pic_height = PictureShow()._position_and_size(
            pic_size, area_size, stretch_small=False
        )
        assert x == 0
        assert y == (area_height - pic_height) / 2
        assert pic_width == area_width
        assert pic_height == pytest.approx(pic_width / aspect_ratio)

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((400, 3260), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((400, 3260), A4_LANDSCAPE_MARGIN_72, id='landscape'),
            pytest.param((1500, 1000), A4_LANDSCAPE_MARGIN_72, id='3:2 landscape'),
            pytest.param(
                (1000, 1500),
                A4_PORTRAIT_MARGIN_72,
                id='2:3 portrait',
                marks=pytest.mark.xfail(
                    raises=AssertionError,
                    reason='picture is taller than page, but not taller than area'
                )
            ),
        )
    )
    def test_big_tall_picture(self, pic_size, area_size):
        aspect_ratio = pic_size[0] / pic_size[1]
        area_width, area_height = area_size
        x, y, pic_width, pic_height = PictureShow()._position_and_size(
            pic_size, area_size, stretch_small=False
        )
        assert x == (area_width - pic_width) / 2
        assert y == 0
        assert pic_width == pytest.approx(pic_height * aspect_ratio)
        assert pic_height == area_height

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((104, 112), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((104, 112), A4_LANDSCAPE_MARGIN_72, id='landscape'),
        )
    )
    def test_small_picture(self, pic_size, area_size):
        area_width, area_height = area_size
        x, y, pic_width, pic_height = PictureShow()._position_and_size(
            pic_size, area_size, stretch_small=False
        )
        assert x == (area_width - pic_width) / 2
        assert y == (area_height - pic_height) / 2
        assert pic_width, pic_height == pic_size

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((192, 108), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((192, 108), A4_LANDSCAPE_MARGIN_72, id='landscape'),
            pytest.param((200, 300), A4_PORTRAIT_MARGIN_72, id='2:3 portrait'),
            pytest.param(
                (300, 200),
                A4_LANDSCAPE_MARGIN_72,
                id='3:2 landscape',
                marks=pytest.mark.xfail(
                    raises=AssertionError,
                    reason='picture is wider than page, but not wider than area'
                )
            ),
        )
    )
    def test_small_wide_picture_stretch_small(self, pic_size, area_size):
        aspect_ratio = pic_size[0] / pic_size[1]
        area_width, area_height = area_size
        x, y, pic_width, pic_height = PictureShow()._position_and_size(
            pic_size, area_size, stretch_small=True
        )
        assert x == 0
        assert y == (area_height - pic_height) / 2
        assert pic_width == area_width
        assert pic_height == pytest.approx(pic_width / aspect_ratio)

    @pytest.mark.parametrize(
        'pic_size, area_size',
        (
            pytest.param((68, 112), A4_PORTRAIT_MARGIN_72, id='portrait'),
            pytest.param((68, 112), A4_LANDSCAPE_MARGIN_72, id='landscape'),
            pytest.param((300, 200), A4_LANDSCAPE_MARGIN_72, id='3:2 landscape'),
            pytest.param(
                (200, 300),
                A4_PORTRAIT_MARGIN_72,
                id='2:3 portrait',
                marks=pytest.mark.xfail(
                    raises=AssertionError,
                    reason='picture is taller than page, but not taller than area'
                )
            ),
        )
    )
    def test_small_tall_picture_stretch_small(self, pic_size, area_size):
        aspect_ratio = pic_size[0] / pic_size[1]
        area_width, area_height = area_size
        x, y, pic_width, pic_height = PictureShow()._position_and_size(
            pic_size, area_size, stretch_small=True
        )
        assert x == (area_width - pic_width) / 2
        assert y == 0
        assert pic_width == pytest.approx(pic_height * aspect_ratio)
        assert pic_height == area_height


class TestAreas:
    """Test core.PictureShow._areas"""

    @pytest.mark.parametrize(
        'layout, expected_height',
        (
            pytest.param((1, 1), A4_LENGTH - 2*72, id='1x1'),
            pytest.param((1, 2), (A4_LENGTH - 3*72) / 2, id='1x2'),
            pytest.param((1, 3), (A4_LENGTH - 4*72) / 3, id='1x3'),
            pytest.param((1, 4), (A4_LENGTH - 5*72) / 4, id='1x4'),
        )
    )
    def test_single_column_layout(self, layout, expected_height):
        page_size, margin = A4, 72
        areas = list(PictureShow()._areas(layout, page_size, margin))

        # number of areas == number of rows
        assert len(areas) == layout[1]

        # the bottom-most area on page has y == margin
        assert areas[-1].y == pytest.approx(margin)

        # all areas have x == margin, width == A4_WIDTH - 2*margin
        assert all(area == pytest.approx(
            (margin, A4_LENGTH - i * (expected_height + margin),
             A4_WIDTH - 2*margin, expected_height),
            abs=1e-4
        )
                   for i, area in enumerate(areas, 1))

    @pytest.mark.parametrize(
        'layout, expected_width',
        (
            pytest.param((1, 1), A4_WIDTH - 144, id='1x1'),
            pytest.param((2, 1), (A4_WIDTH - 216) / 2, id='2x1'),
            pytest.param((3, 1), (A4_WIDTH - 288) / 3, id='3x1'),
            pytest.param((4, 1), (A4_WIDTH - 360) / 4, id='4x1'),
        )
    )
    def test_single_row_layout(self, layout, expected_width):
        page_size, margin = A4, 72
        areas = list(PictureShow()._areas(layout, page_size, margin))

        # number of areas == number of columns
        assert len(areas) == layout[0]

        # the left-most area on page has x == margin
        assert areas[0].x == pytest.approx(margin)

        # all areas have y == margin, height == A4_LENGTH - 2*margin
        assert all(area == pytest.approx(
            (margin + i * (margin + expected_width), margin,
             expected_width, A4_LENGTH - 2*margin),
            abs=1e-4
        )
                   for i, area in enumerate(areas))

    @pytest.mark.parametrize(
        'layout, page_size, margin, expected_width, expected_height',
        (
            pytest.param((3, 3), A4, 18, (A4_WIDTH - 72) / 3,
                         (A4_LENGTH - 72) / 3, id='(3, 3) portrait'),
            pytest.param((3, 3), A4, 0, A4_WIDTH / 3, A4_LENGTH / 3,
                         id='(3, 3) portrait no margin'),
            pytest.param((3, 3), A4_LANDSCAPE, 36, (A4_LENGTH - 144) / 3,
                         (A4_WIDTH - 144) / 3, id='(3, 3) landscape'),
        )
    )
    def test_3x3_layout(self, layout, page_size, margin, expected_width,
                        expected_height):
        areas = list(PictureShow()._areas(layout, page_size, margin))
        assert len(areas) == 9
        assert all(area.width == pytest.approx(expected_width, abs=1e-4)
                   for area in areas)
        assert all(area.height == pytest.approx(expected_height, abs=1e-4)
                   for area in areas)

        # all areas in the left column have x == margin
        assert all(area.x == pytest.approx(margin) for area in areas[::3])

        # all areas in the bottom row have y == margin
        assert all(area.y == pytest.approx(margin) for area in areas[6:])

    @pytest.mark.parametrize(
        'layout, page_size, margin',
        (
            pytest.param((1, 1), A4, A4_WIDTH / 2, id='page width / 2'),
            pytest.param((1, 1), A4_LANDSCAPE, A4_WIDTH / 2,
                         id='page width / 2, landscape'),
            pytest.param((1, 1), A4, A4_WIDTH / 2 + 1, id='page width / 2 + 1'),
            pytest.param((1, 2), A4, A4_LENGTH / 3, id='page length / 3'),
            pytest.param((1, 2), A4_LANDSCAPE, A4_LENGTH / 3,
                         id='page length / 3, landscape'),
            pytest.param((1, 2), A4, A4_LENGTH / 3 + 1, id='page length / 3 + 1'),
            pytest.param((1, 5), A4, A4_LENGTH / 6, id='page length / 6'),
        )
    )
    def test_high_margin_raises_error(self, layout, page_size, margin):
        with pytest.raises(MarginError, match='margin value too high: .+'):
            list(PictureShow()._areas(layout, page_size, margin))


@pytest.mark.parametrize(
    'number, noun, expected',
    (
            pytest.param(1, 'file', '1 file', id='1 file'),
            pytest.param(2, 'file', '2 files', id='2 files'),
            pytest.param(1, 'picture', '1 picture', id='1 picture'),
            pytest.param(3, 'picture', '3 pictures', id='3 pictures'),
            pytest.param(1, 'page', '1 page', id='1 page'),
            pytest.param(4, 'page', '4 pages', id='4 pages'),
            pytest.param(1, 'error', '1 error', id='1 error'),
            pytest.param(5, 'error', '5 errors', id='5 errors'),
    )
)
def test_number(number, noun, expected):
    assert _number(number, noun) == expected
