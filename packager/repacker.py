from enum import Enum
import logging
import re
from typing import Dict, List, Tuple

from packager.constants import DELIMITER_NEWLINE
from packager import rx

LOGGER = logging.getLogger(__name__)


class TranslateType(Enum):
    SIMPLE = "SIMPLE"
    MULTILINE_GENERAL = "MULTILINE_GENERAL"
    MULTILINE_START = "MULTILINE_START"
    MULTILINE_END = "MULTILINE_END"


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

        # Iterate over text file
        with open(self.filename_translate, "r") as translate_fp:
            LOGGER.info(f"|{self.filename_translate_suffix}| Loading into memory...")
            translate_contents = translate_fp.readlines()

        translate_index = self._convert_to_index(translate_contents)

        repack_contents = self._translate(base_contents, translate_index)

        self._write_to_file(repack_contents)

    def _check_file_alignment(self):
        base_root = self.filename_base_suffix.split(".")[0]
        translate_expected = base_root + "_translate.txt"

        if self.filename_translate_suffix != translate_expected:
            raise Exception(
                "File Alignment Mismatch."
                f"Base XML: {self.filename_base_suffix} <-/-> {self.filename_translate_suffix}"
            )

    def _convert_to_index(self, translate_contents: List[str]) -> Dict[int, Tuple[TranslateType, str]]:
        translate_index = {}
        for row in translate_contents:
            match_multiline_general = rx.CIPHER_MULTILINE_GENERAL.match(row)
            match_multiline_start = rx.CIPHER_MULTILINE_START.match(row)
            match_multiline_end = rx.CIPHER_MULTILINE_END.match(row)
            match_simple = rx.CIPHER_SIMPLE.match(row)

            if match_multiline_general:
                match = match_multiline_general
                line_type = TranslateType.MULTILINE_GENERAL
            elif match_multiline_start:
                match = match_multiline_start
                line_type = TranslateType.MULTILINE_START
            elif match_multiline_end:
                match = match_multiline_end
                line_type = TranslateType.MULTILINE_END
            elif match_simple:
                match = match_simple
                line_type = TranslateType.SIMPLE
            else:
                raise Exception(f"Invalid Row format: {row}")

            line_number = int(match.groups()[0])

            # Strip out unpacker added newline at end of line for most line_type cases
            if line_type is not TranslateType.MULTILINE_GENERAL:
                text = row[match.end() + 1:-1]
            else:
                text = row[match.end() + 1:]

            text = self.post_process(text)

            translate_index[line_number] = (line_type, text)

        return translate_index

    @staticmethod
    def post_process(text: str) -> str:
        # Replace DELIMITED newline with text embedded \n character
        text = text.replace(DELIMITER_NEWLINE, "\\n")

        return text

    def _write_to_file(self, file_contents_repacked: List[str]):
        output_filename = f"{self.output_directory}/{self.filename_base_suffix}"
        with open(output_filename, "w", encoding="windows-1251") as output_fp:
            output_fp.writelines(file_contents_repacked)
        LOGGER.info(f"File: {self.filename_base_suffix} - Writing: {output_filename} - Successful")

    def _translate(
        self,
        file_contents: List[str],
        translate_index: Dict[int, Tuple[TranslateType, str]]
    ) -> List[str]:
        repack_contents = file_contents.copy()

        for line_number, (line_type, text_english) in translate_index.items():
            line_xml = repack_contents[line_number - 1]
            if line_type is TranslateType.SIMPLE:
                line_translate = self._text_replace(rx.XML_SIMPLE, text_english, line_xml)
            elif line_type is TranslateType.MULTILINE_GENERAL:
                line_translate = text_english
            elif line_type is TranslateType.MULTILINE_START:
                line_translate = self._text_replace(rx.XML_MULTILINE_START, text_english, line_xml)
            elif line_type is TranslateType.MULTILINE_END:
                line_translate = self._text_replace(rx.XML_MULTILINE_END, text_english, line_xml)
            else:
                raise Exception(f"Invalid TranslateType: {line_type}")

            # Update the file_contents with the translation
            repack_contents[line_number - 1] = line_translate

        return repack_contents

    @staticmethod
    def _text_replace(regex: re.Pattern, text_replace: str, text_old: str):
        r = regex.search(text_old).span(1)
        text_new = text_old[:r[0]] + text_replace + text_old[r[1]:]
        return text_new
