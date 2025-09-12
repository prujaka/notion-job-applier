import pandas as pd


def extract_text(obj: list[dict]):
    return obj[0]['text']['content'] if obj else None


def map_dict(entry: dict) -> dict:
    """Map a Notion API entry to a flattened dictionary format."""
    id = entry['id']
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

    result_dict = {
        'page_id': id,
        'job_title': job_title,
        'company': company,
        'language': language,
        'date_applied': date_applied,
        'origin': origin,
        'stage': stage,
        'job_description': job_description,
        'cover_letter': cover_letter
    }
    return result_dict


def extract_select(column: str, props: dict):
    select_dict = props[column]['select']
    return select_dict['name'] if select_dict else None


def build_dataframe(results: list[dict]) -> pd.DataFrame:
    """Build a dataframe from Notion API raw entries."""
    entries_list = list(map(map_dict, results))
    return pd.DataFrame(entries_list)
