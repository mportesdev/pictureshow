from PIL import UnidentifiedImageError
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


class ReportlabBackend:
    read_errors = (
        OSError,  # file does not exist or is a dir
        UnidentifiedImageError,  # file not recognized as picture
    )

    def init(self, output_file, page_size):
        self.canvas = Canvas(output_file, pagesize=page_size)

    def add_page(self):
        self.canvas.showPage()

    def read_picture(self, picture):
        return ImageReader(picture)

    def get_picture_size(self, picture):
        return picture.getSize()

    def add_picture(self, picture, x, y, width, height):
        self.canvas.drawImage(picture, x, y, width, height, mask='auto')

    def save(self):
        self.canvas.save()
