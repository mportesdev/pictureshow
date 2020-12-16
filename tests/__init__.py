from types import SimpleNamespace

A4_WIDTH = 72 * 210 / 25.4
A4_LENGTH = 72 * 297 / 25.4
A4 = A4_WIDTH, A4_LENGTH
A4_LANDSCAPE = A4_LENGTH, A4_WIDTH

PICS = SimpleNamespace(
    _1_GOOD=('pics/picture.png',),
    _2_GOOD=('pics/picture.png', 'pics/picture.jpg'),
    _2_GOOD_1_BAD=('pics/picture.png', 'pics/samples.pdf', 'pics/picture.jpg'),
    _2_BAD_1_GOOD=('pics/not_jpg.jpg', 'pics/picture.png', 'pics/samples.pdf'),
    _1_BAD=('pics/not_jpg.jpg',),
    _2_BAD=('pics/not_jpg.jpg', 'pics/samples.pdf'),
    DIR=('pics',),
    MISSING=('missing.png',),
)
