import re

XML_SIMPLE = re.compile("<text>(.*)</text>")
XML_MULTILINE_START = re.compile("<text>(.*)")
XML_MULTILINE_END = re.compile("(.*)</text>")

CIPHER_SIMPLE = re.compile(r"\[(\d+)]")
CIPHER_MULTILINE_GENERAL = re.compile(r"\[(\d+)]" + r":(ML):")
CIPHER_MULTILINE_START = re.compile(r"\[(\d+)]" + r":(MLS):")
CIPHER_MULTILINE_END = re.compile(r"\[(\d+)]" + r":(MLE):")
