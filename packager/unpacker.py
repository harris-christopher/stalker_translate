import logging
import os
from typing import List

from packager import rx
from packager.constants import (
    CHARACTER_LIMIT,
    DELIMITER_MULTILINE_GENERAL,
    DELIMITER_MULTILINE_END,
    DELIMITER_MULTILINE_START,
    DELIMITER_NEWLINE,
)

LOGGER = logging.getLogger(__name__)


class Unpacker:
    def __init__(self, filename, dir_output_unpack, dir_input_repack, is_character_limit: bool = False):
        self.filename = filename
        # TODO: Change to os.sep
        self.filename_suffix = self.filename.split("\\")[-1]
        self.dir_output_unpack = dir_output_unpack
        self.dir_input_repack = dir_input_repack

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

            line_iter = enumerate(iter(file_contents), start=1)
            for idx, line in line_iter:
                match_simple = rx.XML_SIMPLE.search(line)
                match_multiline = rx.XML_MULTILINE_START.search(line)

                if match_simple:
                    LOGGER.info(f"|{self.filename_suffix}| [{idx}] Match - Simple")
                    text = self.process_simple_match(match_simple, idx)
                elif match_multiline:
                    LOGGER.info(f"|{self.filename_suffix}| [{idx}] Match - Multiline")
                    text = self.process_multiline_match(match_multiline, idx, line_iter)
                else:
                    LOGGER.info(f"|{self.filename_suffix}| [{idx}] Match - None")
                    continue

                text = self.post_process(text)

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
    def process_simple_match(match, idx: int) -> str:
        processed_text = match.groups()[0] + "\n"
        processed_text_prepended = f"[{idx}] " + processed_text
        return processed_text_prepended

    @staticmethod
    def process_multiline_match(match, idx: int, line_iter) -> str:
        # Handle Starting Line
        match_start = match.groups()[0]
        if match_start:
            prefix_start = f"[{idx}]{DELIMITER_MULTILINE_START} "
            line_to_parse_prepended = prefix_start + match.groups()[0]
            text = line_to_parse_prepended + "\n"
        else:
            text = ""

        # Handle Body (Middle Line(s))
        idx, line_to_parse = next(line_iter)
        while not rx.XML_MULTILINE_END.search(line_to_parse):
            prefix_middle = f"[{idx}]{DELIMITER_MULTILINE_GENERAL} "
            line_to_parse_prepended = prefix_middle + line_to_parse
            text = text + line_to_parse_prepended
            idx, line_to_parse = next(line_iter)

        # Handle Ending Line
        match_end = rx.XML_MULTILINE_END.search(line_to_parse).groups()[0]
        if match_end:
            prefix_end = f"[{idx}]{DELIMITER_MULTILINE_END} "
            line_to_parse_prepended = prefix_end + match_end
            text = text + line_to_parse_prepended + "\n"

        return text

    @staticmethod
    def post_process(text: str) -> str:
        # Replace text embedded \n with delimiter to avoid munging by translator
        text = text.replace("\\n", DELIMITER_NEWLINE + " ")

        return text

    def write_to_file(self, file_contents_unpacked: List[str]):
        filename_no_ext = self.filename_suffix.split(".")[0]
        # Write File Contents to Unpacker Output Directory
        output_filename = f"{self.dir_output_unpack}/{filename_no_ext}_unpacked.txt"
        if self.is_character_limit:
            output_filename = output_filename.replace(".txt", f"-{self.output_file_partition}.txt")
        LOGGER.info(f"File: {self.filename} - Writing: {output_filename} - Characters: {self.characters_written}...")
        with open(output_filename, "w", encoding="windows-1251") as output_fp:
            output_fp.writelines(file_contents_unpacked)
        LOGGER.info(f"File: {self.filename_suffix} - Writing: {output_filename} - Successful")

        self.output_file_partition = self.output_file_partition + 1
        self.characters_written = 0

        # Create Empty File w/ Proper Naming Scheme in Repacker Input Directory
        output_repack_filename = f"{self.dir_input_repack}/{filename_no_ext}_translate.txt"
        if self.is_character_limit:
            output_repack_filename = output_repack_filename.replace(".txt", f"-{self.output_file_partition}.txt")

        with open(output_repack_filename, "w"):
            pass
