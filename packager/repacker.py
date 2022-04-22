from enum import Enum, auto
import logging
from typing import Dict, List, Tuple

from packager import rx

LOGGER = logging.getLogger(__name__)


class TranslateType(Enum):
    SIMPLE = auto()
    MULTILINE_GENERAL = auto()
    MULTILINE_START = auto()
    MULTILINE_END = auto()


class Repacker:
    def __init__(self, filename_base, filename_translate, output_directory):
        self.filename_base = filename_base
        self.filename_translate = filename_translate
        self.filename_base_suffix = self.filename_base.split("\\")[-1]
        self.filename_translate_suffix = self.filename_translate.split("\\")[-1]
        self.output_directory = output_directory

        self._check_file_alignment()

    def repack(self):
        LOGGER.info(f"Repacking... |{self.filename_base_suffix}| <- |{self.filename_translate_suffix}|...")

        # Readlines base & store in array
        with open(self.filename_base, "r", encoding="windows-1251") as base_fp:
            LOGGER.info(f"|{self.filename_base_suffix}| Loading into memory...")
            base_contents = base_fp.readlines()

        repack_contents = base_contents.copy()

        # Iterate over text file
        with open(self.filename_translate, "r") as translate_fp:
            LOGGER.info(f"|{self.filename_translate_suffix}| Loading into memory...")
            translate_contents = translate_fp.readlines()

        translate_index = self._convert_to_index(translate_contents)

        # Use line number for array index (-1 for 0 based indexing)
        for line_translate in translate_contents:
            pass
            # just do simple string replace (regex used depends on line code)
            # TODO: NOTE THIS IS SLIGHTLY MORE COMPLICATED THAN THAT

    def _check_file_alignment(self):
        base_root = self.filename_base_suffix.split(".")[0]
        translate_expected = base_root + "_translate.txt"

        if self.filename_translate_suffix != translate_expected:
            raise Exception(
                "File Alignment Mismatch."
                f"Base XML: {self.filename_base_suffix} <-/-> {self.filename_translate_suffix}"
            )

    @staticmethod
    def _convert_to_index(translate_contents: List[str]) -> Dict[int, Tuple[TranslateType, str]]:
        translate_index = {}
        for row in translate_contents:
            match_multiline_general = rx.CIPHER_MULTILINE_GENERAL.match(row)
            match_multiline_start = rx.CIPHER_MULTILINE_START.match(row)
            match_multiline_end = rx.CIPHER_MULTILINE_END.match(row)
            match_simple = rx.CIPHER_SIMPLE.match(row)

            if match_multiline_general:
                match = match_multiline_general
                line_number = match_multiline_general.groups[0]
                line_type = match_multiline_general.groups[1]
                text = row[match_multiline_general[match_multiline_general.end() + 1]]
                print("ml_general")
                pass
            elif match_multiline_start:
                match = match_multiline_start
                line_number = match_multiline_start.groups[0]
                line_type = match_multiline_start.groups[1]
                print("ml_start")
                pass
            elif match_multiline_end:
                match = match_multiline_end
                line_number = match_multiline_end.groups[0]
                line_type = match_multiline_end.groups[1]
                print("ml_end")
                pass
            elif match_simple:
                match = match_simple
                line_number = match_simple.groups[0]
                print("simple")
                pass
            else:
                raise Exception(f"Invalid Row format: {row}")
