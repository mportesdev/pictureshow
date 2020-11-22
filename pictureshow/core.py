from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


class PictureShow:
    def __init__(self, *pic_files):
        self.pic_files = pic_files

    def save_pdf(self, pdf_file, page_size=A4, margin=0, stretch_small=False):
        page_width, page_height = page_size[0], page_size[1]
        area_width, area_height = page_width - 2*margin, page_height - 2*margin

        pdf_canvas = Canvas(pdf_file, pagesize=page_size)
        for pic_file in self.pic_files:
            picture = ImageReader(pic_file)
            pic_width, pic_height = picture.getSize()
            pic_is_big = pic_width > area_width or pic_height > area_height
            pic_is_wide = pic_width / pic_height > area_width / area_height

            # calculate scale factor to fit picture to area
            if pic_is_big or stretch_small:
                scale = (area_width / pic_width if pic_is_wide
                         else area_height / pic_height)
                pic_width = pic_width * scale
                pic_height = pic_height * scale

            # center picture to area
            x = margin + (area_width - pic_width) / 2
            y = margin + (area_height - pic_height) / 2

            pdf_canvas.drawImage(picture, x, y,
                                 width=pic_width, height=pic_height)
            pdf_canvas.showPage()

        pdf_canvas.save()


def pictures_to_pdf(*pic_files, pdf_file=None, page_size=A4, margin=0,
                    stretch_small=False):
    if pdf_file is None:
        *pic_files, pdf_file = pic_files

    PictureShow(*pic_files).save_pdf(pdf_file, page_size, margin, stretch_small)


def picture_to_pdf(pic_file, pdf_file, page_size=A4, margin=0,
                   stretch_small=False):
    PictureShow(pic_file).save_pdf(pdf_file, page_size, margin, stretch_small)
