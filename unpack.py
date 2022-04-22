import argparse
from glob import glob
import logging
import os

from packager.unpacker import Unpacker

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def type_xml(path: str):
    filenames = glob(path)
    for filename in filenames:
        if not filename.endswith(".xml"):
            raise argparse.ArgumentTypeError(f"File: {filename} is not a valid XML file")
    return path


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def run():
    parser = argparse.ArgumentParser(description="Unpack Russian XML File(s) Into Text w/ Index")
    parser.add_argument(
        "-in",
        help="Russian XML File(s)",
        dest="input",
        type=type_xml,
        required=True,
    )
    parser.add_argument(
        "-out",
        help="Output Directory for Reconstructed Russian Text File(s)",
        dest="output",
        type=dir_path,
        default="output-unpack"
    )
    parser.add_argument(
        "-part",
        help="Partition Files by Character Limit",
        dest="partition",
        type=bool,
        default=False,
    )

    args = parser.parse_args()

    for filename in glob(args.input):
        unpacker = Unpacker(filename, args.output, args.partition)
        unpacker.unpack()


if __name__ == "__main__":
    run()
