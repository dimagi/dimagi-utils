from django.utils.translation import *


class LanguageSwitch():
    def __init__(self, new_lang):
        self.old_lang = get_language()
        self.new_lang = new_lang

    def __enter__(self):
        activate(self.new_lang)

    def __exit__(self, type, value, traceback):
        activate(self.old_lang)


def get_translation(text, lang):
    if text is None:
        return None
    else:
        with LanguageSwitch(lang):
            return ugettext(text)