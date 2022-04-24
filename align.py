import argparse
from glob import glob
import logging
import os

from packager.aligner import Aligner

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def type_txt(path: str):
    filenames = glob(path)
    for filename in filenames:
        if not filename.endswith(".txt"):
            raise argparse.ArgumentTypeError(f"File: {filename} is not a valid TXT file")
    return path


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def run():
    parser = argparse.ArgumentParser(description="Ensure proper translation & repair broken line numbers")
    parser.add_argument(
        "-in-eng",
        help="English TXT File - Unpacker Output + Manual Translation",
        dest="input_english",
        type=type_txt,
        required=True,
    )
    parser.add_argument(
        "-in-rus",
        help="Russian TXT File - Unpacker Primary Output",
        dest="input_russian",
        type=type_txt,
        required=True,
    )
    parser.add_argument(
        "-outdir",
        help="Output Directory for Reconstructed Russian Text File(s)",
        dest="output_align",
        type=dir_path,
        default="output_align"
    )

    args = parser.parse_args()

    aligner = Aligner(glob(args.input_english), glob(args.input_russian), args.output_align)
    aligner.align()


if __name__ == "__main__":
    run()
