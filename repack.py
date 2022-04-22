import argparse
import logging
import os

from packager.repacker import Repacker

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def type_xml(filename: str):
    if not filename.endswith(".xml"):
        raise argparse.ArgumentTypeError(f"File: {filename} is not a valid XML file")
    return filename


def type_txt(filename: str):
    if not filename.endswith(".txt"):
        raise argparse.ArgumentTypeError(f"File: {filename} is not a valid TXT file")
    return filename


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def run():
    parser = argparse.ArgumentParser(description="Unpack Russian XML File(s) Into Text w/ Index")
    parser.add_argument(
        "-base",
        help="Russian XML File",
        dest="base",
        type=type_xml,
        required=True,
    )
    parser.add_argument(
        "-trans",
        help="Translated Text File",
        dest="translate",
        type=type_txt,
        required=True,
    )
    parser.add_argument(
        "-out",
        help="Output Directory For Reconstructed XML File(s)",
        dest="output",
        type=dir_path,
        default="output-repack"
    )

    args = parser.parse_args()

    repacker = Repacker(args.base, args.translate, args.output)
    repacker.repack()


if __name__ == "__main__":
    run()
