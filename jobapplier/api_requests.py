import json

import requests
from requests.models import Response

from jobapplier.cover_letter import build_letter
from jobapplier.data_preprocessing import build_dataframe


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
    results = []
    body = {}

    while has_more:
        if not cursor:
            search_response = requests.post(url=url, headers=headers)
        else:
            search_response = requests.post(url=url, headers=headers, json=body)

        search_response_dict = search_response.json()
        has_more = search_response_dict["has_more"]
        cursor = search_response_dict["next_cursor"]
        body = {"start_cursor": cursor}

        results_loc = search_response_dict["results"]
        results += results_loc

    return results


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
    results = fetch_database_jsons(url=database_url, headers=headers)
    df_full = build_dataframe(results)
    columns = ['page_id', 'job_title', 'company', 'language']
    df_pending = df_full.loc[df_full['stage'].isna(), columns]
    df_pending['cover_letter'] = df_pending.apply(
        lambda row: build_letter(
            row['language'],
            row['company'],
            row['job_title']
        ),
        axis=1
    )

    responses = []
    for index, row in df_pending.iterrows():
        response = add_block(
            text=row['cover_letter'],
            block_id=row['page_id'],
            headers=headers,
            block_type=block_type
        )
        responses.append(response)

    return responses
