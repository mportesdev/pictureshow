import itertools
import os
import re
from collections import namedtuple
from pathlib import Path

from reportlab.lib import pagesizes

from .backends import ReportlabBackend
from .exceptions import LayoutError, MarginError, PageSizeError, RGBColorError

PAGE_SIZES = {
    name: size
    for name, size in vars(pagesizes).items()
    # use isupper() to exclude deprecated names and function names
    if name.isupper()
}

DELIMITER = re.compile('[x,]')

_Box = namedtuple('_Box', 'x y width height')

_Result = namedtuple('_Result', 'num_ok errors num_pages')


class PictureShow:
    def __init__(self, *pic_files):
        self._pic_files = pic_files
        self._backend = ReportlabBackend()

    def save_pdf(
            self,
            output_file,
            *,
            force_overwrite=False,
            page_size='A4',
            landscape=False,
            bg_color=None,
            layout=(1, 1),
            margin=72,
            stretch_small=False,
            fill_cell=False,
    ):
        """Save pictures stored in `self._pic_files` to a PDF document.

        Return a named tuple of three values:
        `num_ok` - number of successfully saved pictures
        `errors` - list of items skipped due to error
        `num_pages` - number of pages of the resulting PDF document
        """
        for _ in self._save_pdf(
                output_file,
                force_overwrite=force_overwrite,
                page_size=page_size,
                landscape=landscape,
                bg_color=bg_color,
                layout=layout,
                margin=margin,
                stretch_small=stretch_small,
                fill_cell=fill_cell,
        ):
            pass
        return self.result

    def _save_pdf(
            self,
            output_file,
            *,
            force_overwrite,
            page_size,
            landscape,
            bg_color,
            layout,
            margin,
            stretch_small,
            fill_cell,
    ):
        output_file = self._validate_target_path(output_file, force_overwrite)
        page_size = self._validate_page_size(page_size, landscape)
        bg_color = self._validate_color(bg_color)
        layout = self._validate_layout(layout)

        self._backend.init(output_file, page_size, bg_color)
        valid_pics = self._valid_pictures()
        self.num_ok = 0
        cells = tuple(self._cells(layout, page_size, margin))
        while True:
            for cell in cells:
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
                pic_box = self._position_and_size(
                    self._backend.get_picture_size(picture),
                    (cell.width, cell.height),
                    stretch_small,
                    fill_cell,
                )
                self._backend.add_picture(
                    picture,
                    position=(cell.x + pic_box.x, cell.y + pic_box.y),
                    size=(pic_box.width, pic_box.height),
                )
                self.num_ok += 1
                yield True
            self._backend.add_page()

    @property
    def result(self):
        return _Result(self.num_ok, self.errors, self.num_pages)

    @staticmethod
    def _validate_target_path(path, force_overwrite):
        path = Path(path)
        if path.exists() and not force_overwrite:
            raise FileExistsError(f'file {os.fspath(path)!r} exists')

        return path

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
            if page_width <= 0 or page_height <= 0:
                raise page_size_error
        except (ValueError, TypeError) as err:
            raise page_size_error from err

        if page_width < page_height and landscape:
            return page_height, page_width
        return page_width, page_height

    @staticmethod
    def _validate_color(color):
        if color is None:
            return None
        try:
            r, g, b = bytes.fromhex(color)
        except (ValueError, TypeError) as err:
            raise RGBColorError('6-digit hex value expected') from err
        return r, g, b

    @staticmethod
    def _validate_layout(layout):
        layout_error = LayoutError('two positive integers expected')
        try:
            if isinstance(layout, str):
                layout = tuple(int(s) for s in DELIMITER.split(layout))
            columns, rows = layout
            if not (
                    isinstance(columns, int) and isinstance(rows, int)
                    and columns > 0 and rows > 0
            ):
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
    def _position_and_size(pic_size, cell_size, stretch_small, fill_cell):
        """Calculate position and size of the picture within the cell."""
        cell_width, cell_height = cell_size
        if fill_cell:
            return _Box(0, 0, cell_width, cell_height)

        pic_width, pic_height = pic_size
        pic_is_big = pic_width > cell_width or pic_height > cell_height

        # calculate scale factor to fit picture to cell
        if pic_is_big or stretch_small:
            pic_is_wide = pic_width / pic_height > cell_width / cell_height
            scale = cell_width / pic_width if pic_is_wide else cell_height / pic_height
            pic_width *= scale
            pic_height *= scale

        # center picture in cell
        x = (cell_width - pic_width) / 2
        y = (cell_height - pic_height) / 2

        return _Box(x, y, pic_width, pic_height)

    @staticmethod
    def _cells(layout, page_size, margin):
        num_columns, num_rows = layout
        page_width, page_height = page_size

        cell_width = (page_width - (num_columns + 1) * margin) / num_columns
        cell_height = (page_height - (num_rows + 1) * margin) / num_rows
        if cell_width < 1 or cell_height < 1:
            raise MarginError(f'margin value too high: {margin}')

        cells_y_coords = (
            page_height - row * (cell_height + margin)
            for row in range(1, num_rows + 1)
        )
        cells_x_coords = (
            margin + col * (cell_width + margin)
            for col in range(num_columns)
        )
        # yield cells row-wise
        for y, x in itertools.product(cells_y_coords, cells_x_coords):
            yield _Box(x, y, cell_width, cell_height)


def pictures_to_pdf(
        *pic_files,
        output_file,
        force_overwrite=False,
        page_size='A4',
        landscape=False,
        bg_color=None,
        layout=(1, 1),
        margin=72,
        stretch_small=False,
        fill_cell=False,
):
    """Save one or more pictures to a PDF document.

    Return a named tuple of three values:
    `num_ok` - number of successfully saved pictures
    `errors` - list of items skipped due to error
    `num_pages` - number of pages of the resulting PDF document
    """
    pic_show = PictureShow(*pic_files)

    return pic_show.save_pdf(
        output_file,
        force_overwrite=force_overwrite,
        page_size=page_size,
        landscape=landscape,
        bg_color=bg_color,
        layout=layout,
        margin=margin,
        stretch_small=stretch_small,
        fill_cell=fill_cell,
    )
