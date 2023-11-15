import itertools
import re
from collections import namedtuple
from pathlib import Path

from reportlab.lib import pagesizes

from .backends import ReportlabBackend
from .exceptions import LayoutError, MarginError, PageSizeError

PAGE_SIZES = {
    name: size
    for name, size in vars(pagesizes).items()
    # use isupper() to exclude deprecated names and function names
    if name.isupper()
}

DELIMITER = re.compile('[x,]')

DrawingArea = namedtuple('DrawingArea', 'x y width height')

Result = namedtuple('Result', 'num_ok errors num_pages')


class PictureShow:
    def __init__(self, *pic_files):
        self._pic_files = pic_files
        self._backend = ReportlabBackend()

    def save_pdf(self, output_file, page_size='A4', landscape=False, margin=72,
                 layout=(1, 1), stretch_small=False, fill_area=False,
                 force_overwrite=False):
        """Save pictures stored in `self._pic_files` to a PDF document.

        Return a named tuple of three values:
        `num_ok` - number of successfully saved pictures
        `errors` - list of items skipped due to error
        `num_pages` - number of pages of the resulting PDF document
        """
        for _ in self._save_pdf(
            output_file, page_size, landscape, margin, layout, stretch_small,
            fill_area, force_overwrite
        ):
            pass
        return self.result

    def _save_pdf(self, output_file, page_size, landscape, margin, layout,
                  stretch_small, fill_area, force_overwrite):
        output_file = self._validate_target_path(output_file, force_overwrite)
        page_size = self._validate_page_size(page_size, landscape)
        layout = self._validate_layout(layout)

        self._backend.init(output_file, page_size)
        valid_pics = self._valid_pictures()
        self.num_ok = 0
        areas = tuple(self._areas(layout, page_size, margin))
        while True:
            for area in areas:
                try:
                    while True:
                        picture = next(valid_pics)
                        if picture is not None:
                            break
                        yield False
                except StopIteration:
                    if self.num_ok > 0:
                        self._backend.save()
                    self.num_pages = self._backend.num_pages
                    return
                x, y, pic_width, pic_height = self._position_and_size(
                    self._backend.get_picture_size(picture),
                    area[2:],    # short for (area.width, area.height)
                    stretch_small,
                    fill_area
                )
                self._backend.add_picture(
                    picture, area.x + x, area.y + y, pic_width, pic_height
                )
                self.num_ok += 1
                yield True
            self._backend.add_page()

    @property
    def result(self):
        return Result(self.num_ok, self.errors, self.num_pages)

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
        for pic_file in self._pic_files:
            try:
                picture = self._backend.read_picture(pic_file)
            except self._backend.read_errors as err:
                self.errors.append((pic_file, err))
                yield None
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
