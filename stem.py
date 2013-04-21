"""Module for working with words"""

import pymorphy2
from stemming.porter2 import stem

morph = pymorphy2.MorphAnalyzer()


def lemmatize_ru(str):
	"""
	Lemmatize russian words
	"""
	global morph

	try:
		p = morph.parse(str)[0]
	except IndexError:
		return str
	return p.normal_form

def lemmatize_en(str):
	"""
	Lemmatize english words
	"""
	return stem(str)

class lemmatizer:
    languages = set({"ru", "en"})
    def __init__(self, lang = None):
        if (lang in lemmatizer.languages):
            self.lang = lang
        else:
            self.lang = None

    def get(self):
        if (self.lang == "ru"):
            return lemmatize_ru
        elif (self.lang == "en"):
            return lemmatize_en
        else:
            return None