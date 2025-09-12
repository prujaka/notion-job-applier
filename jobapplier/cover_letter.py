import unicodedata
import pandas as pd
import os

from jobapplier.constants import (LETTER_TEMPLATE_PATH_EN, DATA_PATH,
                                  LETTER_TEMPLATE_PATH_FR)


def starts_with_vowel(word: str) -> bool:
    """Return True if the word starts with a vowel (supports accents)."""
    word = word.strip()
    if not word:
        return False

    first_char = word[0].lower()
    normalized = unicodedata.normalize('NFD', first_char)
    base_letter = normalized[0]

    return base_letter in 'aeiouy'


def build_letter_config(company: str, title: str) -> dict:
    """Return letter config dict for English and French templates."""
    configs = {
        'EN': {
            'template_file': LETTER_TEMPLATE_PATH_EN,
            'replacements': {
                'COMPANY NAME': company,
                'JOB TITLE': title,
            },
            'article_before_title': ('as a ', 'as an ')
        },
        'FR': {
            'template_file': LETTER_TEMPLATE_PATH_FR,
            'replacements': {
                'NOM D’ENTREPRISE': company,
                'TITRE DU POSTE': title,
            },
            'article_before_title': ('en tant que ', "en tant qu'"),
            'de_phrase': ('de ', "d'")
        }
    }
    return configs


def build_letter(lang: str, company: str, title: str) -> str:
    """Build a personalized cover letter from a template.

    This function selects the appropriate letter template based on the
    language, replaces placeholders with the company and job title, and
    adjusts articles before words that start with vowels. In French,
    it also contracts the 'de' preposition before vowel-initial company
    names.

    Parameters
    ----------
    lang : str
        Language code of the letter template. Must be either 'EN' or 'FR'.
    company : str
        The name of the company to include in the letter.
    title : str
        The job title to include in the letter.

    Returns
    -------
    str
        The completed cover letter text with placeholders replaced and
        language-specific corrections applied.

    Raises
    ------
    ValueError
        If `lang` is not one of the supported values ('EN', 'FR').
    """
    configs = build_letter_config(company, title)

    if lang not in configs:
        raise ValueError(f"The language selected: '{lang}'."
                         "Please select lang value from ['EN', 'FR'].")

    config = configs[lang]
    template_file_path = configs[lang]['template_file']

    with open(template_file_path, 'r', encoding='utf-8') as f:
        letter = f.read()
        for placeholder, value in config['replacements'].items():
            letter = letter.replace(placeholder, value)

    article, vowel_article = config['article_before_title']
    title_phrase = f"{article}{title}"
    if starts_with_vowel(title):
        corrected_phrase = f"{vowel_article}{title}"
        letter = letter.replace(title_phrase, corrected_phrase)

    if lang == 'FR' and starts_with_vowel(company):
        de_phrase, de_contracted = config['de_phrase']
        original_phrase = f"{de_phrase}{company}"
        corrected_phrase = f"{de_contracted}{company}"
        letter = letter.replace(original_phrase, corrected_phrase)

    return letter


# TODO: remove this function after it's not needed
def add_cover_letters_csv(listings_init_csv: str,
                          listings_with_covers_csv: str) -> None:
    df_listings = pd.read_csv(DATA_PATH.joinpath(listings_init_csv))
    df_listings['cover_letter'] = df_listings.apply(
        lambda row: build_letter(row['language'], row['company_name'],
                                 row['job_title']), axis=1
    )
    df_listings.to_csv(DATA_PATH.joinpath(listings_with_covers_csv),
                       index=False)


if __name__ == '__main__':
    os.chdir('..')
    print(build_letter("FR", "COMPANY", "JOB"))
