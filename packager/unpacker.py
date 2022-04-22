import logging
import re
from typing import List


LOGGER = logging.getLogger(__name__)

RX_SIMPLE = re.compile("<text>(.*)</text>")
RX_MULTILINE_START = re.compile("<text>(.*)")
RX_MULTILINE_END = re.compile("(.*)</text>")
CHARACTER_LIMIT = 5000
NEWLINE_EDITOR_DELIMITER = "<NL_ED>"
NEWLINE_TEXT_DELIMITER = "<NL_TXT>"


class Unpacker:
    def __init__(self, filename, output_directory, is_character_limit: bool = False):
        self.filename = filename
        self.filename_suffix = self.filename.split("\\")[-1]
        self.output_directory = output_directory

        # Character Limit Settings
        self.is_character_limit = is_character_limit
        self.output_file_partition = 0
        self.characters_written = 0

    def unpack(self):
        LOGGER.info(f"|{self.filename_suffix}| - Unpacking...")
        text_unpacked = []

        with open(self.filename, "r", encoding="windows-1251") as input_fp:
            LOGGER.info(f"|{self.filename_suffix}| Loading into memory...")
            file_contents = input_fp.readlines()

            line_iter = enumerate(iter(file_contents))
            for line_no, line in line_iter:
                match_simple = RX_SIMPLE.search(line)
                match_multiline = RX_MULTILINE_START.search(line)

                if match_simple:
                    LOGGER.info(f"|{self.filename_suffix}| [{line_no}] Match - Simple")
                    text = self.process_simple_match(match_simple)
                elif match_multiline:
                    LOGGER.info(f"|{self.filename_suffix}| [{line_no}] Match - Multiline")
                    text = self.process_multiline_match(match_multiline, line_iter)
                else:
                    LOGGER.info(f"|{self.filename_suffix}| [{line_no}] Match - None")
                    continue

                text = text.replace("\\n", NEWLINE_TEXT_DELIMITER)

                if self.is_character_limit:
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

    @staticmethod
    def process_simple_match(match) -> str:
        return match.groups()[0] + "\n"

    @staticmethod
    def process_multiline_match(match, line_iter) -> str:
        text = match.groups()[0] if match.groups() else ""

        _, line_to_parse = next(line_iter)
        while not RX_MULTILINE_END.search(line_to_parse):
            text = text + line_to_parse.replace("\n", NEWLINE_EDITOR_DELIMITER)
            _, line_to_parse = next(line_iter)

        match_end = RX_MULTILINE_END.search(line_to_parse)
        text = text + match_end.groups()[0] if match_end.groups() else text

        return text + "\n"

    def write_to_file(self, file_contents_unpacked: List[str]):
        output_filename = f"{self.output_directory}/{self.filename_suffix}-unpacked.txt"
        if self.is_character_limit:
            output_filename = output_filename.replace(".txt", f"-{self.output_file_partition}.txt")
        LOGGER.info(f"File: {self.filename} - Writing: {output_filename} - Characters: {self.characters_written}...")
        with open(output_filename, "w", encoding="windows-1251") as output_fp:
            output_fp.writelines(file_contents_unpacked)
        LOGGER.info(f"File: {self.filename_suffix} - Writing: {output_filename} - Successful")

        self.output_file_partition = self.output_file_partition + 1
        self.characters_written = 0
