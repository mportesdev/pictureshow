import argparse
import os

from pictureshow import picture_to_pdf


def main():
    parser = argparse.ArgumentParser('pictureshow')
    parser.add_argument('-i', '--picture', '--infile',
                        help='input file', required=True)
    parser.add_argument('-o', '--pdf', '--outfile',
                        help='output file', required=True)
    args = parser.parse_args()

    picture_path = os.path.abspath(args.picture)
    pdf_path = os.path.abspath(args.pdf)

    picture_to_pdf(picture_path, pdf_path)
