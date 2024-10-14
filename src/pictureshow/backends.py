import os

from PIL import UnidentifiedImageError
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


class ReportlabBackend:
    read_errors = (
        OSError,  # file does not exist or is a dir
        UnidentifiedImageError,  # file not recognized as picture
    )

    def init(self, output_file, page_size, bg_color=None):
        self._canvas = Canvas(os.fspath(output_file), pagesize=page_size)
        self._page_size = page_size
        self._bg_color = self._calculate_color(bg_color)
        self.num_pages = 0
        self._current_page_empty = True

    @staticmethod
    def _calculate_color(color):
        if color is None:
            return None
        return tuple(n / 255 for n in color)

    def add_page(self):
        self._canvas.showPage()
        self.num_pages += 1
        self._current_page_empty = True

    def read_picture(self, picture):
        return ImageReader(picture)

    def get_picture_size(self, picture):
        return picture.getSize()

    def add_picture(self, picture, position, size):
        if self._current_page_empty:
            if self._bg_color is not None:
                self._canvas.setFillColor(self._bg_color)
                self._canvas.rect(0, 0, *self._page_size, stroke=0, fill=1)
            self._current_page_empty = False
        self._canvas.drawImage(picture, *position, *size, mask='auto')

    def save(self):
        self._canvas.save()
        if not self._current_page_empty:
            self.num_pages += 1
