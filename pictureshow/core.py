from collections import namedtuple
from pathlib import Path

from reportlab.lib import pagesizes
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from pictureshow import PageSizeError, MarginError, LayoutError

DrawingArea = namedtuple('DrawingArea', 'x y width height')


class PictureShow:
    def __init__(self, *pic_files):
        self.pic_files = pic_files
        self.errors = 0

    def save_pdf(self, pdf_file, page_size='A4', landscape=False, margin=72,
                 layout=(1, 1), stretch_small=False, force_overwrite=False):
        if Path(pdf_file).exists() and not force_overwrite:
            raise FileExistsError(f'file {pdf_file!r} exists')

        page_size = self._validate_page_size(page_size, landscape)
        layout = self._validate_layout(layout)

        return self._save_pdf(pdf_file, page_size, margin, layout, stretch_small)

    def _save_pdf(self, pdf_file, page_size, margin, layout, stretch_small):
        pdf_canvas = Canvas(pdf_file, pagesize=page_size)
        valid_pics = self._valid_pictures()
        num_ok, self.errors = 0, 0
        areas = tuple(self._areas(layout, page_size, margin))
        while True:
            for area in areas:
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

    @staticmethod
    def _validate_page_size(page_size, landscape):
        if isinstance(page_size, str):
            try:
                # use upper() to exclude deprecated names and function names
                page_size = getattr(pagesizes, page_size.upper())
            except AttributeError as err:
                raise PageSizeError(f'unknown page size: {page_size}') from err

        try:
            page_width, page_height = page_size
            if page_width < page_height and landscape:
                page_size = page_height, page_width
        except (ValueError, TypeError) as err:
            raise PageSizeError('two positive floats expected') from err

        return page_size

    @staticmethod
    def _validate_layout(layout):
        try:
            if isinstance(layout, str):
                layout = tuple(int(s) for s in layout.split('x'))
            columns, rows = layout
            assert columns > 0 and isinstance(columns, int)
            assert rows > 0 and isinstance(rows, int)
        except (ValueError, AssertionError, TypeError) as err:
            raise LayoutError('two positive integers expected') from err

        return columns, rows

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
    def _areas(layout, page_size, margin):
        columns, rows = layout
        page_width, page_height = page_size

        margins_too_wide = margin * (columns + 1) >= page_width
        margins_too_high = margin * (rows + 1) >= page_height
        if margins_too_wide or margins_too_high:
            raise MarginError(f'margin value too high: {margin}')

        area_width = (page_width - (columns + 1) * margin) / columns
        area_height = (page_height - (rows + 1) * margin) / rows

        for row in range(1, rows + 1):
            area_y = page_height - row * (area_height + margin)
            for col in range(columns):
                area_x = margin + col * (area_width + margin)
                yield DrawingArea(area_x, area_y, area_width, area_height)


def pictures_to_pdf(*pic_files, pdf_file=None, page_size='A4',
                    landscape=False, margin=72, layout=(1, 1),
                    stretch_small=False, force_overwrite=False):
    if pdf_file is None:
        *pic_files, pdf_file = pic_files

    pic_show = PictureShow(*pic_files)
    return pic_show.save_pdf(
        pdf_file, page_size, landscape, margin, layout, stretch_small,
        force_overwrite
    )
