import json

import pandas as pd
import requests
from requests.models import Response

from jobapplier.cover_letter import build_letter
from jobapplier.data_preprocessing import build_dataframe, is_cleaned_substring


def stage_is_none(entry: dict) -> bool:
    """Check whether the 'Stage' property of a JSON entry is None."""
    return entry['properties']['Stage']['select'] is None


def build_rich_text(text: str):
    """Build a Notion rich text JSON object from a plain text string.

    If the input text's length exceeds 2000 characters, it is broken into
    chunks.
    """

    max_len = 2000
    chunks = [text[i:i + max_len] for i in range(0, len(text), max_len)]
    rich_text = [{
        "type": "text",
        "text": {
            "content": chunk
        }
    } for chunk in chunks]
    return rich_text


def build_codeblock_json(text: str):
    """Build a Notion code block JSON object from a plain text string."""
    rich_text = build_rich_text(text)
    children = {
        "children": [
            {
                "object": "block",
                "type": "code",
                "code": {
                    "caption": [],
                    "rich_text": rich_text,
                    "language": "plain text"
                }
            }
        ]
    }

    return children


def build_paragraph_json(text: str) -> dict:
    """Build a Notion paragraph JSON object from a plain text string."""
    rich_text = build_rich_text(text)
    children = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text
                }
            }
        ]
    }
    return children


def add_block(
        text: str,
        block_id: str,
        headers: dict,
        block_type: str
) -> Response:
    """Append a block to the specified Notion block or page.

    Reference: https://developers.notion.com/reference/patch-block-children

    Parameters
    ----------
    text : str
        The text content to include in the block.
    block_id : str
        The ID of the parent block or page to append the code block to.
    headers : str
        Notion API headers for a PATCH request.
    block_type : str
        Type of Notion block to create. Supported values: 'code', 'paragraph'.

    Returns
    -------
    Response
        The HTTP response object returned by the Notion API.
    """
    if block_type == 'code':
        children = build_codeblock_json(text)
    elif block_type == 'paragraph':
        children = build_paragraph_json(text)
    else:
        children = build_paragraph_json(text)
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.patch(url, headers=headers, data=json.dumps(children))
    return response


def fetch_database_jsons(url: str, headers: dict) -> list:
    """Fetch all JSON entries from a Notion database and return them as a list.

    Parameters
    ----------
    url : str
        The Notion API endpoint URL for querying the database.
    headers : dict
        A dictionary of HTTP headers including authorization and version info.

    Returns
    -------
    list
        A list of all database entry objects returned by the Notion API.
    """
    has_more = True
    cursor = None
    all_pages = []
    body = {}

    while has_more:
        if cursor:
            body = {"start_cursor": cursor}
        search_response = requests.post(url=url, headers=headers, json=body)
        search_response.raise_for_status()
        data = search_response.json()
        all_pages.extend(data["results"])
        has_more = data["has_more"]
        cursor = data.get("next_cursor")

    return all_pages


def add_cover_letters(
        database_url: str,
        headers: dict,
        block_type: str | None
) -> list:
    """Generate and append cover letters to Notion entries missing a 'stage'
    value.

    This function:
    1. Fetches entries from the provided Notion database URL.
    2. Filters for entries where the 'stage' property is not set.
    3. Builds a cover letter using language, company, and job title.
    4. Appends each cover letter as a Notion block (e.g., paragraph or code).

    Parameters
    ----------
    database_url : str
        The URL of the Notion database to query.
    headers : dict
        HTTP headers for Notion API requests, including authorization and
        version info.
    block_type : str or None
        The Notion block type to use when appending the cover letter. Can
        be either 'paragraph' or 'code'.

    Returns
    -------
    list of Response
        A list of HTTP response objects from the Notion API, one for each
        appended block.
    """
    print("Fetching database with Notion's API...")
    results = fetch_database_jsons(url=database_url, headers=headers)
    print("Database successfully fetched.")
    df_full = build_dataframe(results)
    columns = ['page_id', 'job_title', 'company', 'language']
    df_pending = df_full.loc[
        df_full['stage'].isna() & df_full['language'].notna(), columns
    ]
    df_pending['cover_letter'] = df_pending.apply(
        lambda row: build_letter(
            row['language'],
            row['company'],
            row['job_title']
        ),
        axis=1
    )

    responses = []
    for i, (index, row) in enumerate(df_pending.iterrows()):
        response = add_block(
            text=row['cover_letter'],
            block_id=row['page_id'],
            headers=headers,
            block_type=block_type
        )
        responses.append(response)
        print(f'{i + 1}. Cover letter added to {row['job_title']}'
              f' at {row['company']}')

    print("Cover letters are generated and added to the Notion database.")

    return responses


def company_substring_entries(
        substring: str,
        url: str,
        headers: dict
) -> pd.DataFrame:
    """Return entries where company contains the given substring."""
    results = fetch_database_jsons(url=url, headers=headers)
    df_jobs = build_dataframe(results)
    columns = ['job_title', 'company', 'date_applied', 'origin', 'stage']
    df_containing_substring = df_jobs.loc[
        df_jobs['company'].map(lambda x: is_cleaned_substring(substring, x)),
        columns
    ]
    return df_containing_substring


def assign_positions(database_url: str, headers: dict,
                     position_property: str = "Position", dry_run: bool = True):
    """Assign reversed order numbers to all database entries based on query
    order.

    Parameters
    ----------
    database_url : str
        The Notion API database query endpoint, e.g.
        "https://api.notion.com/v1/databases/<db_id>/query".
    headers : dict
        Headers including Authorization, Notion-Version, and Content-Type.
    position_property : str
        The name of the Number property to update.
    dry_run : bool
        If True, only prints the planned updates without sending PATCH requests.
    """
    all_pages = fetch_database_jsons(url=database_url, headers=headers)
    total = len(all_pages)

    for idx, page in enumerate(all_pages):
        page_id = page['id']
        position_value = total - idx  # reverse order
        props = page['properties']

        def get_text(prop_name):
            if prop_name in props and props[prop_name]['type'] == 'title':
                return ''.join(
                    [t['plain_text'] for t in props[prop_name]['title']])
            if prop_name in props and props[prop_name]['type'] == 'rich_text':
                return ''.join(
                    [t['plain_text'] for t in props[prop_name]['rich_text']])
            if prop_name in props and props[prop_name]['type'] == 'date':
                return props[prop_name]['date']['start']
            return ''

        job_title = get_text('Job Title')
        company = get_text('Company')
        date_applied = get_text('Date Applied')

        print(f'Planned: {position_value} ← {job_title} @ {company} '
              f'(applied {date_applied}) [{page_id}]')

        if not dry_run:
            update_url = f'https://api.notion.com/v1/pages/{page_id}'
            update_payload = {
                'properties': {position_property: {'number': position_value}}}
            resp = requests.patch(update_url, headers=headers,
                                  json=update_payload)
            resp.raise_for_status()
            print(f'Updated: {position_value} ← {job_title} @ {company}'
                  f' (applied {date_applied})')
