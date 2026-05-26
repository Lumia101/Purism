import re
import unicodedata
import html
from ftfy import fix_text

class UnicodeCleaner():
    def __init__(self, type="NFC": str):
        method = ["NFC", "NFD", "NFKC", "NFKD"]
        if type in method:
            self.unicode_type = type
        else:
            raise ValueError("Invalid Unicode Normalization method. Available method: ["NFC", "NFD", "NFKC", "NFKD"]")

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        cleaned_text = unicodedata.normalize(self.unicode_type, text)
        return cleaned_text

class UICleaner():
    def __init__(self):
        self.html_tag_re = re.compile(r'<[^>]+>')
        self.control_char_re = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        text = html.unescape(text)
        text = self.html_tag_re.sub(" ", text)
        text = self.control_char_re.sub("", text)

        return text

class TextCleaner():
    def __init__(self):
        self.whitespace_re = re.compile(r'\s+')
        self.repeat_re = re.compile(r"(ㅋ|ㅎ|ㅠ|ㅜ|!|\.)\1{2,}")

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        text = fix_text(text)
        text = self.repeat_re.sub(r"\1\1", text)
        text = self.whitespace_re.sub(" ", text).strip()

        return text
