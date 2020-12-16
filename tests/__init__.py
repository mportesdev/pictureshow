from types import SimpleNamespace

A4_WIDTH = 72 * 210 / 25.4
A4_LENGTH = 72 * 297 / 25.4
A4 = A4_WIDTH, A4_LENGTH
A4_LANDSCAPE = A4_LENGTH, A4_WIDTH
A4_PORTRAIT_MARGIN_72 = (A4_WIDTH - 144, A4_LENGTH - 144)
A4_LANDSCAPE_MARGIN_72 = (A4_LENGTH - 144, A4_WIDTH - 144)

PICS = SimpleNamespace(
    _1_GOOD=('pics/picture.png',),
    _2_GOOD=('pics/picture.png', 'pics/picture.jpg'),
    _2_GOOD_1_BAD=('pics/picture.png', 'pics/samples.pdf', 'pics/picture.jpg'),
    _1_BAD=('pics/not_jpg.jpg',),
)
