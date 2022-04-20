import argparse
import logging
import os
import re
from typing import List

import deepl

AUTH_KEY = "c74da11c-7113-125c-70dd-870ce82ecf59:fx"
RX_TRANS = re.compile("<text>(.*)</text>")

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def xml_file(path):
    if os.path.isfile(path) and path.endswith(".xml"):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid XML file")


def run():
    parser = argparse.ArgumentParser(description="Convert XML File(s) w/ Russian Text to English Text.")
    parser.add_argument("-in", help="Input XML File", dest="input", type=xml_file, required=True)
    parser.add_argument("-out", help="Output directory", dest="output", type=dir_path, required=True)

    args = parser.parse_args()

    xmltrans(args.input, args.output)


def xmltrans(input_filename: str, output_dir: str):

    LOGGER.info("Configuring DeepL Translator...")
    translator_deepl = deepl.Translator(AUTH_KEY)
    LOGGER.info("Configuring DeepL Translator... Done!")

    # # Retrieve list of XML files in directory
    # input_filenames = glob(path_input_files)
    # input_filenames_xml = [input_filename for input_filename in input_filenames if input_filename.endswith(".xml")]

    # Translate the content of XML file
    with open(input_filename, "r", encoding="windows-1251") as input_fp:
        LOGGER.info(f"Loading file: {input_filename} into memory...")
        file_contents = input_fp.readlines()
        LOGGER.info("Beginning File Translation...")
        file_contents_translate = process_text(file_contents, translator_deepl)
        LOGGER.info("File Translation Complete!")

        output_filename = f"{output_dir}/{input_filename.split('/')[-1]}"
        LOGGER.info(f"Writing Translation to output file: {output_filename}")
        with open(output_filename, "w", encoding="utf-8") as output_fp:
            output_fp.writelines(file_contents_translate)

        LOGGER.info(f"XML Translation for file: {input_filename} -> {output_filename} complete!")


def process_text(text: List[str], translator_deepl: deepl.Translator) -> List[str]:
    text_processed = []
    for idx, line in enumerate(text):
        LOGGER.info(f"Processing line: {idx}...")
        # Find the text in the line to be translated
        matches = RX_TRANS.search(line)
        if matches:

            # If we have more than a single match - there is a formatting issue
            if isinstance(matches.group(), tuple):
                match_count = len(matches.group())
                LOGGER.error(f"{match_count} matches found for line: {idx}: {line}")
                raise Exception(f"Multiple matches found for line: {idx}: {line}")

            LOGGER.info(f"Processing line: {idx} - MATCH FOUND!")
            # The actual translation work - call the DeepL API
            text_raw = matches.group(1)
            text_translate = translator_deepl.translate_text(text_raw, target_lang="EN-US")
            text_translate = text_translate.text

            LOGGER.info(
                f"Processing line: {idx}:"
                f"{text_raw}"
                "->"
                f"{text_translate}"
            )
            line_translate = line.replace(text_raw, text_translate)
            text_processed.append(line_translate)
        else:
            LOGGER.info(f"Processing line: {idx} - no match found")
            LOGGER.info(f"{line}")
            text_processed.append(line)

    return text_processed


if __name__ == "__main__":
    run()
