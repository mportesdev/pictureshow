from reportlab.pdfgen.canvas import Canvas


class ReportlabBackend:
    def init(self, output_file, page_size):
        self.canvas = Canvas(output_file, pagesize=page_size)

    def add_page(self):
        self.canvas.showPage()

    def add_picture(self, picture, x, y, width, height):
        self.canvas.drawImage(picture, x, y, width, height, mask='auto')

    def save(self):
        self.canvas.save()
