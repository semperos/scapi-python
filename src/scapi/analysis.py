from io import FileIO
from typing import Any

import pandas as pd
import requests

from scapi.util import guess_mime_type

from .api import Formatter

array_fields: list[str] = [
    "branch_ids",
    "comment_ids",
    "commit_ids",
    "custom_field_value_ids",
    "epic_ids",
    "file_ids",
    "follower_ids",
    "group_ids",
    "group_mention_ids",
    "iteration_ids",
    "key_result_ids",
    "label_ids",
    "linked_file_ids",
    "member_ids",
    "member_mention_ids",
    "mention_ids",
    "merged_branch_ids",
    "object_story_link_ids",
    "objective_ids",
    "owner_ids",
    "permission_ids",
    "previous_iteration_ids",
    "project_ids",
    "pull_request_ids",
    "story_ids",
    "subject_story_link_ids",
    "task_ids",
    "workflow_ids",
]


def from_response(response: requests.Response) -> pd.DataFrame:
    return pd.DataFrame(response.json())


def flatten(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flattens the given DataFrame by exploding fields that Shortcut's API
    returns as arrays within entities, e.g., follower_ids.
    """
    for array_field in array_fields:
        df = df.explode(array_field)
    return df


class PandasFormatter(Formatter):
    def object(self, response: requests.Response) -> Any:
        return pd.DataFrame(response.json())

    def string(self, response: requests.Response) -> str:
        return pd.DataFrame(response.json()).to_string()  # type: ignore

    def write(self, file: FileIO, response: requests.Response) -> Any:
        mimetype = guess_mime_type(file.name)
        df = pd.DataFrame(response.json())
        match mimetype:
            case "application/vnd.apache.parquet":
                return df.to_parquet(file)
            case "text/csv":
                return df.to_csv(file)
            case "text/tab-separated-values":
                return df.to_csv(file, sep="\t")
            case _:
                return df.to_csv(file)
