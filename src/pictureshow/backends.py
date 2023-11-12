from PIL import UnidentifiedImageError
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


class ReportlabBackend:
    read_errors = (
        OSError,  # file does not exist or is a dir
        UnidentifiedImageError,  # file not recognized as picture
    )

    def init(self, output_file, page_size):
        self._canvas = Canvas(output_file, pagesize=page_size)
        self.num_pages = 0

    def add_page(self):
        self._canvas.showPage()
        self.num_pages += 1
        self._current_page_empty = True

    def read_picture(self, picture):
        return ImageReader(picture)

    def get_picture_size(self, picture):
        return picture.getSize()

    def add_picture(self, picture, x, y, width, height):
        self._canvas.drawImage(picture, x, y, width, height, mask='auto')
        self._current_page_empty = False

    def save(self):
        self._canvas.save()
        if not self._current_page_empty:
            self.num_pages += 1
