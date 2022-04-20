import logging
import re
from typing import List


LOGGER = logging.getLogger(__name__)

RX_SIMPLE = re.compile("<text>(.*)</text>")
# RX_MULTILINE = re.compile("<text>(.*)</text>")
CHARACTER_LIMIT = 5000


class Unpacker:
    def __init__(self, filename, output_directory):
        self.filename = filename
        self.output_directory = output_directory
        self.output_file_partition = 0
        self.characters_written = 0
        # self.index = 0

    def unpack(self):
        LOGGER.info(f"File: {self.filename} - Beginning Unpacking...")
        text_unpacked = []

        with open(self.filename, "r", encoding="windows-1251") as input_fp:
            LOGGER.info(f"Loading file: {self.filename} into memory...")
            file_contents = input_fp.readlines()

            for line_no, line in enumerate(file_contents):
                LOGGER.info(f"File: {self.filename} - Processing line: {line_no}...")

                match = RX_SIMPLE.search(line)

                # CASE: NO TRANSLATE
                if not match:
                    LOGGER.info(f"File: {self.filename}: Line: {line_no} - Nothing to Translate")
                    continue

                text = match.groups()[0] + "\n"

                # Write existing data to file if text will overflow character limit
                if self.characters_written + len(text) >= CHARACTER_LIMIT:
                    self.write_to_file(text_unpacked)
                    text_unpacked = []

                # Add Unpacked Text to Internal Memory Store & Update Characters Written
                text_unpacked.append(text)
                self.characters_written = self.characters_written + len(text)

            # Final flush of unpacked data
            if text_unpacked:
                self.write_to_file(text_unpacked)

    def write_to_file(self, file_contents_unpacked: List[str]):
        filename_suffix = self.filename.split("\\")[-1]
        with open(
            f"{self.output_directory}/{filename_suffix}-unpacked-{self.output_file_partition}.txt",
            "w",
            encoding="windows-1251",
        ) as output_fp:
            output_fp.writelines(file_contents_unpacked)

        self.output_file_partition = self.output_file_partition + 1
        self.characters_written = 0
