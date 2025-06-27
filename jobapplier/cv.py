import string
from nltk.tokenize import word_tokenize
from unidecode import unidecode


def get_sep(lang: str):
    if lang == 'FR':
        return '-'
    elif lang == 'EN':
        return '_'
    else:
        raise KeyError("Please choose the language from ['EN', 'FR']")


def cvfy(text: str, lang: str) -> str:
    text = text.replace('/', ' ')
    for c in string.punctuation:
        text = text.replace(c, '')
    for c in string.digits:
        text = text.replace(c, '')
    text = unidecode(text)
    text = text.lower()
    tokens = word_tokenize(text)
    sep = get_sep(lang)
    text = sep.join(tokens)
    return f'cv{sep}{text}'
