import pytest

from pictureshow.backends import ReportlabBackend


class TestReportlabBackend:
    def test_calculate_color_default(self):
        assert ReportlabBackend._calculate_color(None) is None

    @pytest.mark.parametrize(
        'color, expected',
        (
            pytest.param((0, 0, 0), (0, 0, 0), id='000000'),
            pytest.param((255, 140, 0), (1, 0.549020, 0), id='ff8c00'),
        )
    )
    def test_calculate_color_valid_color(self, color, expected):
        assert ReportlabBackend._calculate_color(color) == pytest.approx(expected)
