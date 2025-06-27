import unicodedata
import os


def starts_with_vowel(word: str) -> bool:
    """Check if the word starts with a vowel (includes accented letters)."""
    word = word.strip()
    if not word:
        return False

    first_char = word[0].lower()

    normalized = unicodedata.normalize('NFD', first_char)
    base_letter = normalized[0]

    return base_letter in 'aeiouy'


def build_letter(lang: str, company: str, title: str) -> str:
    templates = {
        'EN': {
            'file': 'en_template.txt',
            'replacements': {
                'COMPANY NAME': company,
                'JOB TITLE': title,
            },
            'article_before_title': ('as a ', 'as an ')
        },
        'FR': {
            'file': 'fr_template.txt',
            'replacements': {
                'NOM D’ENTREPRISE': company,
                'TITRE DU POSTE': title,
            },
            'article_before_title': ('en tant que ', "en tant qu'"),
            'de_phrase': ('de ', "d'")
        }
    }

    if lang not in templates:
        raise ValueError("Please select lang value from ['EN', 'FR'].")

    config = templates[lang]
    file_path = os.path.join(os.getcwd(), config['file'])

    with open(file_path, 'r', encoding='utf-8') as f:
        letter = f.read()

    for placeholder, value in config['replacements'].items():
        letter = letter.replace(placeholder, value)

    # Handle article before job title
    article, vowel_article = config['article_before_title']
    title_phrase = f"{article}{title}"
    if starts_with_vowel(title):
        corrected_phrase = f"{vowel_article}{title}"
        letter = letter.replace(title_phrase, corrected_phrase)

    # Handle "de NOM D’ENTREPRISE" → "d’NOM D’ENTREPRISE" in French
    if lang == 'FR' and starts_with_vowel(company):
        de_phrase, de_contracted = config['de_phrase']
        original_phrase = f"{de_phrase}{company}"
        corrected_phrase = f"{de_contracted}{company}"
        letter = letter.replace(original_phrase, corrected_phrase)

    return letter
