import argparse
import os

from pictureshow import picture_to_pdf


def main():
    parser = argparse.ArgumentParser('pictureshow')
    parser.add_argument('-i', '--input', '--picture',
                        dest='picture', required=True, help='input file path')
    parser.add_argument('-o', '--output', '--pdf',
                        dest='pdf', required=True, help='output file path')
    args = parser.parse_args()

    picture_path = os.path.abspath(args.picture)
    pdf_path = os.path.abspath(args.pdf)

    picture_to_pdf(picture_path, pdf_path)
    print(f'Saved to file: {pdf_path}')
