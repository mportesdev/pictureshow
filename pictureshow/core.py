from collections import namedtuple
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from pictureshow import PageOrientationError, MarginError

DrawingArea = namedtuple('DrawingArea', 'x y width height')


class PictureShow:
    def __init__(self, *pic_files):
        self.pic_files = pic_files

    def save_pdf(self, pdf_file, page_size=A4, orientation='portrait',
                 margin=72, layout=(1, 1), stretch_small=False,
                 force_overwrite=False):
        if Path(pdf_file).exists() and not force_overwrite:
            raise FileExistsError(f'file {pdf_file!r} exists')

        return self._save_pdf(
            pdf_file, page_size, orientation, margin, layout, stretch_small
        )

    def _save_pdf(self, pdf_file, page_size, orientation, margin, layout,
                  stretch_small):
        if orientation == 'portrait':
            pass
        elif orientation == 'landscape':
            page_size = page_size[::-1]
        else:
            raise PageOrientationError("must be 'portrait' or 'landscape'")

        pdf_canvas = Canvas(pdf_file, pagesize=page_size)
        valid_pics = self._valid_pictures()
        num_ok, self.errors = 0, 0
        while True:
            for area in self._areas(layout, page_size, margin):
                try:
                    picture = next(valid_pics)
                except StopIteration:
                    if num_ok != 0:
                        pdf_canvas.save()
                    return num_ok, self.errors
                x, y, pic_width, pic_height = self._position_and_size(
                    picture.getSize(), (area.width, area.height), stretch_small
                )
                pdf_canvas.drawImage(
                    picture, area.x + x, area.y + y, pic_width, pic_height
                )
                num_ok += 1
            pdf_canvas.showPage()

    def _valid_pictures(self):
        for pic_file in self.pic_files:
            try:
                picture = ImageReader(pic_file)
            except Exception:
                self.errors += 1
                continue
            else:
                yield picture

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

    @staticmethod
    def _areas(page_layout, page_size, margin):
        columns, rows = page_layout
        page_width, page_height = page_size

        margins_too_wide = margin * (columns + 1) >= page_width
        margins_too_high = margin * (rows + 1) >= page_height
        if margins_too_wide or margins_too_high:
            raise MarginError('margin value too high')

        area_width = (page_width - (columns + 1) * margin) / columns
        area_height = (page_height - (rows + 1) * margin) / rows

        for row in range(1, rows + 1):
            area_y = page_height - row * (area_height + margin)
            for col in range(1, columns + 1):
                area_x = page_width - col * (area_width + margin)
                yield DrawingArea(area_x, area_y, area_width, area_height)


def pictures_to_pdf(*pic_files, pdf_file=None, page_size=A4,
                    orientation='portrait', margin=72, layout=(1, 1),
                    stretch_small=False, force_overwrite=False):
    if pdf_file is None:
        *pic_files, pdf_file = pic_files

    pic_show = PictureShow(*pic_files)
    return pic_show.save_pdf(
        pdf_file, page_size, orientation, margin, layout, stretch_small,
        force_overwrite
    )
