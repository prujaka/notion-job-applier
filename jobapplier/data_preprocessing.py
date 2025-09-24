import pandas as pd
from unidecode import unidecode


def is_cleaned_substring(substring: str, string: str) -> bool:
    return unidecode(str(substring).lower()) in unidecode(str(string).lower())


def extract_text(obj: list[dict]):
    """Extract text content from the first item of a Notion rich text list."""
    return obj[0]['text']['content'] if obj else None


def extract_select(column_name: str, props: dict):
    """Extract the option name from a Notion select property by column name."""
    select_dict = props[column_name]['select']
    return select_dict['name'] if select_dict else None


def extract_number(column_name: str, props: dict):
    return props[column_name]['number']


def map_dict(entry: dict) -> dict:
    """Map a Notion API entry to a flattened dictionary format."""
    _id = entry['id']
    props = entry['properties']

    company = extract_text(props['Company']['rich_text'])
    job_title = extract_text(props['Job Title']['title'])
    job_description = extract_text(props['Job Description']['rich_text'])

    date = props['Date Applied']['date']
    date_applied = date['start'] if date else None

    origin = extract_select('Origin', props)
    stage = extract_select('Stage', props)
    language = extract_select('Language', props)
    cover_letter = extract_select('Cover letter', props)
    position = extract_number('Position', props)

    result_dict = {
        'page_id': _id,
        'job_title': job_title,
        'company': company,
        'language': language,
        'date_applied': date_applied,
        'origin': origin,
        'stage': stage,
        'job_description': job_description,
        'cover_letter': cover_letter,
        'position': position,
    }
    return result_dict


def build_dataframe(results: list[dict]) -> pd.DataFrame:
    """Build a dataframe from Notion API raw entries."""
    entries_list = list(map(map_dict, results))
    return pd.DataFrame(entries_list)
