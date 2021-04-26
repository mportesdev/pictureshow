from collections import namedtuple
from pathlib import Path
import re

from PIL import UnidentifiedImageError
from reportlab.lib import pagesizes
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from pictureshow import PageSizeError, MarginError, LayoutError

PAGE_SIZES = {
    name: size
    for name, size in pagesizes.__dict__.items()
    # use isupper() to exclude deprecated names and function names
    if name.isupper()
}

DELIMITER = re.compile('[x,]')

DrawingArea = namedtuple('DrawingArea', 'x y width height')

Result = namedtuple('Result', 'num_ok errors num_pages')


class PictureShow:
    def __init__(self, *pic_files):
        self.pic_files = pic_files
        self.errors = []

    def save_pdf(self, pdf_file, page_size='A4', landscape=False, margin=72,
                 layout=(1, 1), stretch_small=False, force_overwrite=False):
        target_str = self._validate_target_path(pdf_file, force_overwrite)
        page_size = self._validate_page_size(page_size, landscape)
        layout = self._validate_layout(layout)

        return self._save_pdf(
            target_str, page_size, margin, layout, stretch_small
        )

    def _save_pdf(self, pdf_file, page_size, margin, layout, stretch_small):
        pdf_canvas = Canvas(pdf_file, pagesize=page_size)
        valid_pics = self._valid_pictures()
        num_ok = 0
        num_pages = 0
        areas = tuple(self._areas(layout, page_size, margin))
        while True:
            last_page_empty = True
            for area in areas:
                try:
                    picture = next(valid_pics)
                except StopIteration:
                    if not last_page_empty:
                        num_pages += 1
                    if num_ok != 0:
                        pdf_canvas.save()
                    return Result(num_ok, self.errors, num_pages)
                x, y, pic_width, pic_height = self._position_and_size(
                    picture.getSize(), (area.width, area.height), stretch_small
                )
                pdf_canvas.drawImage(
                    picture, area.x + x, area.y + y, pic_width, pic_height,
                    mask='auto'
                )
                last_page_empty = False
                num_ok += 1
            pdf_canvas.showPage()
            num_pages += 1

    @staticmethod
    def _validate_target_path(file_path, force_overwrite):
        target_str = str(file_path)
        target_path = Path(file_path)

        if target_path.exists() and not force_overwrite:
            raise FileExistsError(f'file {target_str!r} exists')

        return target_str

    @staticmethod
    def _validate_page_size(page_size, landscape):
        if isinstance(page_size, str):
            try:
                page_size = PAGE_SIZES[page_size.upper()]
            except KeyError as err:
                raise PageSizeError(
                    f'unknown page size {page_size!r},'
                    f' please use one of: {", ".join(PAGE_SIZES)}'
                ) from err

        page_size_error = PageSizeError('two positive numbers expected')
        try:
            page_width, page_height = page_size
            if not (page_width > 0 and page_height > 0):
                raise page_size_error
        except (ValueError, TypeError) as err:
            raise page_size_error from err

        if page_width < page_height and landscape:
            page_size = page_height, page_width
        return page_size

    @staticmethod
    def _validate_layout(layout):
        layout_error = LayoutError('two positive integers expected')
        try:
            if isinstance(layout, str):
                layout = tuple(int(s) for s in DELIMITER.split(layout))
            columns, rows = layout
            if not (columns > 0 and isinstance(columns, int)
                    and rows > 0 and isinstance(rows, int)):
                raise layout_error
        except (ValueError, TypeError) as err:
            raise layout_error from err

        return columns, rows

    def _valid_pictures(self):
        self.errors = []
        for pic_file in self.pic_files:
            try:
                picture = ImageReader(pic_file)
            except (UnidentifiedImageError, OSError) as err:
                # UnidentifiedImageError: file not recognized as picture
                # OSError: file does not exist or is a dir
                self.errors.append((pic_file, err))
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


def pictures_to_pdf(*pic_files, pdf_file, page_size='A4', landscape=False,
                    margin=72, layout=(1, 1), stretch_small=False,
                    force_overwrite=False):
    pic_show = PictureShow(*pic_files)

    return pic_show.save_pdf(
        pdf_file, page_size, landscape, margin, layout, stretch_small,
        force_overwrite
    )
