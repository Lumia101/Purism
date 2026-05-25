import re
import unicodedata
import html
from ftfy import fix_text

class Normalizer():
    def __init__(self):
        self.html_tag_re = re.compile(r'<[^>]+>')
        self.whitespace_re = re.compile(r'\s+')
        self.control_char_re = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')
        self.repeat_re = re.compile(r"(ㅋ|ㅎ|ㅠ|ㅜ|!|\.)\1{2,}")

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        text = fix_text(text)
        text = html.unescape(text)
        text = self.html_tag_re.sub(" ", text)
        text = unicodedata.normalize("NFC", text)
        text = self.control_char_re.sub("", text)
        text = self.repeat_re.sub(r"\1\1", text)
        text = self.whitespace_re.sub(" ", text).strip()

        return text

if __name__ == "__main__":
    normalizer = Normalizer()
    dirty_text = "<b>안녕하세요!!</b>   반갑습니당\n\n\n  Ã«안녕하세요 &nbsp; ㅋㅋㅋㅋㅋㅋㅋㅋ"
    
    clean_text = normalizer.normalize(dirty_text)
    print(f"Original: {dirty_text}")
    print(f"Cleaned: {clean_text}")