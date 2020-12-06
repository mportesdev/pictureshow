from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from pictureshow.exceptions import PageOrientationError, MarginError


class PictureShow:
    def __init__(self, *pic_files):
        self.pic_files = pic_files

    def save_pdf(self, pdf_file, page_size=A4, orientation='portrait',
                 margin=72, stretch_small=False, force_overwrite=False):
        if Path(pdf_file).exists() and not force_overwrite:
            raise FileExistsError(f'file {pdf_file!r} exists')

        return self._save_pdf(
            pdf_file, page_size, orientation, margin, stretch_small
        )

    def _save_pdf(self, pdf_file, page_size, orientation, margin, stretch_small):
        if orientation == 'portrait':
            pass
        elif orientation == 'landscape':
            page_size = page_size[::-1]
        else:
            raise PageOrientationError("must be 'portrait' or 'landscape'")

        area_size = page_size[0] - 2*margin, page_size[1] - 2*margin
        if min(area_size) <= 0:
            raise MarginError('margin value too high')

        pdf_canvas = Canvas(pdf_file, pagesize=page_size)
        ok, errors = 0, 0
        for pic_file in self.pic_files:
            try:
                picture = ImageReader(pic_file)
            except Exception:
                errors += 1
                continue

            x, y, pic_width, pic_height = self._position_and_size(
                picture.getSize(), area_size, stretch_small
            )
            pdf_canvas.drawImage(
                picture, margin + x, margin + y, pic_width, pic_height
            )
            pdf_canvas.showPage()
            ok += 1

        if ok != 0:
            pdf_canvas.save()
        return ok, errors

    @staticmethod
    def _position_and_size(pic_size, area_size, stretch_small):
        """Calculate position and size of the picture in the area."""
        pic_width, pic_height = pic_size
        area_width, area_height = area_size

        pic_is_big = pic_width > area_width or pic_height > area_height
        pic_is_wide = pic_width / pic_height > area_width / area_height

        # calculate scale factor to fit picture to area
        if pic_is_big or stretch_small:
            scale = (area_width / pic_width if pic_is_wide
                     else area_height / pic_height)
            pic_width = pic_width * scale
            pic_height = pic_height * scale

        # center picture to area
        x = (area_width - pic_width) / 2
        y = (area_height - pic_height) / 2

        return x, y, pic_width, pic_height


def pictures_to_pdf(*pic_files, pdf_file=None, page_size=A4,
                    orientation='portrait', margin=72, stretch_small=False,
                    force_overwrite=False):
    if pdf_file is None:
        *pic_files, pdf_file = pic_files

    pic_show = PictureShow(*pic_files)
    return pic_show.save_pdf(
        pdf_file, page_size, orientation, margin, stretch_small, force_overwrite
    )
