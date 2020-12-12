import pytest

from pictureshow import PictureShow
from tests import A4_WIDTH, A4_LENGTH, A4, A4_LANDSCAPE


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
        areas = list(PictureShow._areas(layout, page_size, margin))

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
        areas = list(PictureShow._areas(layout, page_size, margin))

        # number of areas == number of columns
        assert len(areas) == layout[0]

        # the left-most area on page has x == margin
        assert areas[0].x == pytest.approx(margin)

        # all areas have y == margin, height == A4_LENGTH - 2*margin
        assert all(area == pytest.approx(
            (margin + i * (margin + expected_width), margin, expected_width, A4_LENGTH - 2*margin),
            abs=1e-4
        )
                   for i, area in enumerate(areas))

    @pytest.mark.parametrize(
        'page_size, margin, expected_width, expected_height',
        (
            pytest.param(A4, 18, (A4_WIDTH - 72) / 3, (A4_LENGTH - 72) / 3,
                         id='3x3 portrait'),
            pytest.param(A4, 0, A4_WIDTH / 3, A4_LENGTH / 3,
                         id='3x3 portrait no margin'),
            pytest.param(A4_LANDSCAPE, 36, (A4_LENGTH - 144) / 3,
                         (A4_WIDTH - 144) / 3, id='3x3 landscape'),
        )
    )
    def test_3x3_layout(self, page_size, margin, expected_width,
                        expected_height):
        layout = (3, 3)
        areas = list(PictureShow._areas(layout, page_size, margin))
        assert len(areas) == 9
        assert all(area.width == pytest.approx(expected_width, abs=1e-4)
                   for area in areas)
        assert all(area.height == pytest.approx(expected_height, abs=1e-4)
                   for area in areas)

        # all areas in the left column have x == margin
        assert all(area.x == pytest.approx(margin) for area in areas[::3])

        # all areas in the bottom row have y == margin
        assert all(area.y == pytest.approx(margin) for area in areas[6:])
