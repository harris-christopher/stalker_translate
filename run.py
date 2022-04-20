import argparse
from glob import glob
import logging
import os

from packager.unpacker import Unpacker

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
    LOGGER.info("ass")
    parser = argparse.ArgumentParser(description="Unpack Russian XML File(s) Into Text w/ Index")
    parser.add_argument("-in", help="Input XML File(s)", dest="input", type=type_xml, required=True)
    parser.add_argument("-out", help="Output directory", dest="output", type=dir_path, required=True)

    args = parser.parse_args()

    for filename in glob(args.input):
        unpacker = Unpacker(filename, args.output)
        unpacker.unpack()


if __name__ == "__main__":
    run()
