import logging
import os
import re
from typing import Dict, List
LOGGER = logging.getLogger(__name__)

RX_LINE_PREFIX = re.compile(r"\[(\d+)](?::(ML[ES]?):)?")
# RX_LINE_REDUNDANT = re.compile(r"\[d*].*(\[\d+])")
RX_LINE_REDUNDANT = re.compile(r"\[.*(\[\d+])")
RX_LINE_NO_MALFORMED = re.compile(r"(\[\d+)[^]]")


class Aligner:
    def __init__(self, filenames_base: List[str], filenames_anchor: List[str], output_directory: str):
        self.map_filenames_base: Dict[str, str] = self._generate_lookup(filenames_base)
        self.map_filenames_anchor: Dict[str, str] = self._generate_lookup(filenames_anchor)
        self.output_directory = output_directory

        if len(filenames_base) is not len(filenames_anchor):
            raise Exception(
                "File Count Mismatch."
                f"English: {len(filenames_base)}"
                f"Russian: {len(filenames_anchor)}"
            )

    def align(self):
        LOGGER.info("Beginning File Alignment: " + str(self.map_filenames_base.keys()))

        for filename_base_root, filename_base in self.map_filenames_base.items():
            LOGGER.info(f"{filename_base_root}: Processing...")

            LOGGER.info(f"{filename_base_root}: Retrieving Anchor File")
            filename_anchor = self.map_filenames_anchor[filename_base_root]

            LOGGER.info(f"{filename_base_root}: Loading base into memory...")
            contents_base = self._read_file(filename_base)

            LOGGER.info(f"{filename_base_root}: Loading anchor into memory...")
            contents_anchor = self._read_file(filename_anchor)

            LOGGER.info(f"{filename_base_root}: Verifying Line Count...")
            if len(contents_base) != len(contents_anchor):
                raise Exception(
                    "Line Count Mismatch."
                    f"{filename_base}: {len(contents_base)}"
                    f"{filename_anchor}: {len(contents_anchor)}"
                )

            LOGGER.info(f"{filename_base_root}: Repairing...")
            contents_base_repair = self._repair_text(contents_base, contents_anchor)

            LOGGER.info(f"{filename_base_root}: Writing Repaired File...")
            self._write_to_file(contents_base_repair, filename_base_root)

            LOGGER.info(f"{filename_base_root}: Alignment Successful")

    @staticmethod
    def _generate_lookup(filenames: List[str]) -> Dict[str, str]:
        """
        Retrieves "parallel" Russian file.
        Will be used as ground truth for line numbers and file size.
        """
        lookup = {}
        for filename in filenames:
            filename_suffix = filename.split(os.path.sep)[-1]
            filename_root_array = filename_suffix.split("_")[:-1]
            filename_root = "_".join(filename_root_array)
            lookup[filename_root] = filename

        return lookup

    @staticmethod
    def _read_file(filename: str, encoding: str = "windows-1251") -> List[str]:
        contents = []
        with open(filename, "r", encoding=encoding, errors="ignore") as base_fp:
            for line in base_fp:
                # print(filename + line)
                if line.strip():
                    contents.append(line)

        return contents

    def _repair_text(self, contents_base: List[str], contents_anchor: List[str]) -> List[str]:
        contents_base_repair = contents_base.copy()

        # Repair Mangled Line Numbers
        iter_base = iter(enumerate(contents_base))
        iter_anchor = iter(enumerate(contents_anchor))

        idx_base, line_base = next(iter_base)
        idx_anchor, line_anchor = next(iter_anchor)

        while True:
            line_base_update = self._verify_or_repair_line(line_base, line_anchor)
            contents_base_repair[idx_base] = line_base_update
            try:
                idx_base, line_base = next(iter_base)
                idx_anchor, line_anchor = next(iter_anchor)
            except StopIteration:
                break

        return contents_base_repair

    def _verify_or_repair_line(self, line_base: str, line_anchor: str) -> str:
        match_base = RX_LINE_PREFIX.match(line_base)
        match_anchor = RX_LINE_PREFIX.match(line_anchor)

        line_base = self._remove_redundancy(line_base)

        if match_base:
            if match_base.groups() != match_anchor.groups():
                match_line_base = match_base.groups(1)
                match_line_anchor = match_anchor.groups(1)
                raise Exception(
                    "File Alignment Error - Invalid Match"
                    f"{match_line_base}: Base: {match_base.groups()}"
                    f"{match_line_anchor}: Base: {match_anchor.groups()}"
                )
            line_repair = line_base
        elif RX_LINE_NO_MALFORMED.match(line_base):
            line_repair = self._text_replace(RX_LINE_NO_MALFORMED, match_anchor.group() + " ", line_base)
        elif line_base[0] == "[":
            line_repair = line_base.replace("[", match_anchor.group() + " ")
        else:
            raise Exception(
                "File Alignment Error - Invalid Case"
                f"Base: {line_base}"
                f"Anchor: {line_anchor}"
            )

        return line_repair

    @staticmethod
    def _remove_redundancy(line: str) -> str:
        """
        Remove any consistently munged data from line.
        This supports the consistent (but uncommon) case in a line
          where the line number appears again in the middle of the line.
            ex: [150] This is the issue I am talking about. [150] ;NEW_LINE;
        :param line:
        :return:
        """

        match = RX_LINE_REDUNDANT.search(line)
        if match:
            r = match.span(1)
            line_new = line[:r[0]] + " ;NEW_LINE; " + line[r[1]:]
            return line_new
        else:
            return line

    def _write_to_file(self, contents: List[str], filename_root: str):
        filename_write = f"{self.output_directory}{os.path.sep}{filename_root}_aligned.txt"
        with open(filename_write, "w", encoding="windows-1251") as fp_write:
            fp_write.writelines(contents)

    @staticmethod
    def _text_replace(regex: re.Pattern, text_replace: str, text_old: str):
        r = regex.search(text_old).span(1)
        text_new = text_old[:r[0]] + text_replace + text_old[r[1]:]
        return text_new
