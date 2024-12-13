import typing

import pandas as pd
import responses

from scapi.analysis import PandasFormatter
from scapi.api import ShortcutClient

example_epics = [
    {
        "app_url": "https://app.shortcut.com/testworkspace/epics/123",
        "archived": False,
        "completed": True,
        "completed_at": "2016-12-31T12:30:00Z",
        "created_at": "2016-12-31T12:30:00Z",
        "deadline": "2017-01-01T12:30:00Z",
        "description": "Epic 123",
        "entity_type": "epic",
        "epic_state_id": 987,
        "follower_ids": ["12345678-9012-3456-7890-123456789012"],
        "group_ids": ["12345678-9012-3456-7890-123456789012"],
        "id": 123,
        "label_ids": [567, 678, 890],
        "name": "Epic 123",
        "owner_ids": ["12345678-9012-3456-7890-123456789012"],
        "planned_start_date": "2016-12-31T12:30:00Z",
        "requested_by_id": "12345678-9012-3456-7890-123456789012",
        "started": True,
        "started_at": "2016-11-30T12:30:00Z",
        "state": "done",
        "updated_at": "2020-12-31T12:30:00Z",
    },
    {
        "app_url": "https://app.shortcut.com/testworkspace/epics/234",
        "archived": True,
        "completed": True,
        "completed_at": "2016-12-31T12:30:00Z",
        "created_at": "2016-12-31T12:30:00Z",
        "deadline": "2017-01-01T12:30:00Z",
        "description": "Epic 123",
        "entity_type": "epic",
        "epic_state_id": 987,
        "follower_ids": ["12345678-9012-3456-7890-123456789012"],
        "group_ids": ["12345678-9012-3456-7890-123456789012"],
        "id": 234,
        "label_ids": [567, 678],
        "name": "Epic 234",
        "owner_ids": ["12345678-9012-3456-7890-123456789012"],
        "planned_start_date": "2016-12-31T12:30:00Z",
        "requested_by_id": "12345678-9012-3456-7890-123456789012",
        "started": True,
        "started_at": "2016-11-30T12:30:00Z",
        "state": "done",
        "updated_at": "2020-12-31T12:30:00Z",
    },
]


@responses.activate
def test_pandas_formatter_standalone():
    client = ShortcutClient(token="testtoken")
    path = "/epics"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp_json = example_epics
    resp = responses.Response(
        method="GET",
        url=url,
        status=200,
        json=resp_json,
    )
    responses.add(resp)
    x = client.get("/epics")
    pf = PandasFormatter()
    df = typing.cast(pd.DataFrame, pf.object(x))
    assert (2, 21) == df.shape
    assert df[df["archived"]].shape == (1, 21)
