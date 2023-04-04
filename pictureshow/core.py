import itertools
import re
from collections import namedtuple
from pathlib import Path

from PIL import UnidentifiedImageError
from reportlab.lib import pagesizes
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from .exceptions import PageSizeError, MarginError, LayoutError

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

    def save_pdf(self, output_file, page_size='A4', landscape=False, margin=72,
                 layout=(1, 1), stretch_small=False, fill_area=False,
                 force_overwrite=False):
        """Save pictures stored in `self.pic_files` to a PDF document.

        Return a named tuple of three values:
        `num_ok` - number of successfully saved pictures
        `errors` - list of items skipped due to error
        `num_pages` - number of pages of the resulting PDF document
        """
        output_file = self._validate_target_path(output_file, force_overwrite)
        page_size = self._validate_page_size(page_size, landscape)
        layout = self._validate_layout(layout)

        return self._save_pdf(
            output_file, page_size, margin, layout, stretch_small, fill_area
        )

    def _save_pdf(self, output_file, page_size, margin, layout, stretch_small,
                  fill_area):
        pdf_canvas = Canvas(output_file, pagesize=page_size)
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
                    if num_ok > 0:
                        pdf_canvas.save()
                    return Result(num_ok, self.errors, num_pages)
                x, y, pic_width, pic_height = self._position_and_size(
                    picture.getSize(),
                    area[2:],    # short for (area.width, area.height)
                    stretch_small,
                    fill_area
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
    def _validate_target_path(path, force_overwrite):
        target_str = str(path)
        target_path = Path(path)

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

        error = PageSizeError('two positive numbers expected')
        try:
            page_width, page_height = page_size
            if not (page_width > 0 and page_height > 0):
                raise error
        except (ValueError, TypeError) as err:
            raise error from err

        if page_width < page_height and landscape:
            page_size = page_height, page_width
        return page_size

    @staticmethod
    def _validate_layout(layout):
        error = LayoutError('two positive integers expected')
        try:
            if isinstance(layout, str):
                layout = tuple(int(s) for s in DELIMITER.split(layout))
            columns, rows = layout
            if not (columns > 0 and isinstance(columns, int)
                    and rows > 0 and isinstance(rows, int)):
                raise error
        except (ValueError, TypeError) as err:
            raise error from err

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
    def _position_and_size(pic_size, area_size, stretch_small, fill_area):
        """Calculate position and size of the picture in the area."""
        area_width, area_height = area_size
        if fill_area:
            return 0, 0, area_width, area_height

        pic_width, pic_height = pic_size
        pic_is_big = pic_width > area_width or pic_height > area_height
        pic_is_wide = pic_width / pic_height > area_width / area_height

        # calculate scale factor to fit picture to area
        if pic_is_big or stretch_small:
            scale = (area_width / pic_width if pic_is_wide
                     else area_height / pic_height)
            pic_width *= scale
            pic_height *= scale

        # center picture to area
        x = (area_width - pic_width) / 2
        y = (area_height - pic_height) / 2

        return x, y, pic_width, pic_height

    @staticmethod
    def _areas(layout, page_size, margin):
        num_columns, num_rows = layout
        page_width, page_height = page_size

        area_width = (page_width - (num_columns + 1) * margin) / num_columns
        area_height = (page_height - (num_rows + 1) * margin) / num_rows
        if area_width < 1 or area_height < 1:
            raise MarginError(f'margin value too high: {margin}')

        areas_y_coords = (
            page_height - row * (area_height + margin)
            for row in range(1, num_rows + 1)
        )
        areas_x_coords = (
            margin + col * (area_width + margin)
            for col in range(num_columns)
        )
        # yield areas row-wise
        for y, x in itertools.product(areas_y_coords, areas_x_coords):
            yield DrawingArea(x, y, area_width, area_height)


def pictures_to_pdf(*pic_files, output_file, page_size='A4', landscape=False,
                    margin=72, layout=(1, 1), stretch_small=False, fill_area=False,
                    force_overwrite=False):
    """Save one or more pictures to a PDF document.

    Return a named tuple of three values:
    `num_ok` - number of successfully saved pictures
    `errors` - list of items skipped due to error
    `num_pages` - number of pages of the resulting PDF document
    """
    pic_show = PictureShow(*pic_files)

    return pic_show.save_pdf(
        output_file, page_size, landscape, margin, layout, stretch_small, fill_area,
        force_overwrite
    )
