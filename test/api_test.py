import pytest
import requests
import responses

from scapi import ShortcutClient

testClient = ShortcutClient(token="testtoken")

exited = False


def test_validate():
    assert testClient.validate() == testClient
    badClient = ShortcutClient(token=None)
    x = []
    badClient.validate(exit_callback=lambda: x.append(42))  # type: ignore
    assert x == [42]


@responses.activate
def test_sc_get_ok():
    path = "/member"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp_json = {
        "id": "12345678-9012-3456-7890-123456789012",
        "mention_name": "testmention_name",
        "name": "Test Testerson",
        "workspace2": {"estimate_scale": [0, 1, 2], "url_slug": "testworkspace2"},
    }
    resp = responses.Response(
        method="GET",
        url=url,
        status=200,
        json=resp_json,
    )
    responses.add(resp)
    assert testClient.get(path).json() == resp_json


@responses.activate
def test_sc_get_not_ok():
    path = "/member"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp = responses.Response(
        method="GET",
        url=url,
        status=422,
    )
    responses.add(resp)
    with pytest.raises(requests.HTTPError):
        testClient.get(path)


@responses.activate
def test_sc_delete_ok():
    path = "/epics/42"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp = responses.Response(
        method="DELETE",
        url=url,
        status=204,
        body="",
    )
    responses.add(resp)
    actual: requests.Response = testClient.delete(path)
    assert actual.status_code == 204


@responses.activate
def test_sc_delete_not_ok():
    path = "/epics/42"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp = responses.Response(
        method="DELETE",
        url=url,
        status=422,
    )
    responses.add(resp)
    with pytest.raises(requests.HTTPError):
        testClient.delete(path)


@responses.activate
def test_sc_post_ok():
    path = "/labels"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp_json = {
        "app_url": "https://app.shortcut.com/test-workspace2/labels/123",
        "archived": True,
        "color": "#6515dd",
        "created_at": "2016-12-31T12:30:00Z",
        "description": "test",
        "entity_type": "label",
        "external_id": None,
        "id": 123,
        "name": "testlabel",
        "stats": {
            "num_epics": 123,
            "num_epics_completed": 123,
            "num_epics_in_progress": 123,
            "num_epics_total": 123,
            "num_epics_unstarted": 123,
            "num_points_backlog": 123,
            "num_points_completed": 123,
            "num_points_in_progress": 123,
            "num_points_total": 123,
            "num_points_unstarted": 123,
            "num_related_documents": 123,
            "num_stories_backlog": 123,
            "num_stories_completed": 123,
            "num_stories_in_progress": 123,
            "num_stories_total": 123,
            "num_stories_unestimated": 123,
            "num_stories_unstarted": 123,
        },
        "updated_at": "2016-12-31T12:30:00Z",
    }
    resp = responses.Response(
        method="POST",
        url=url,
        status=201,
        json=resp_json,
    )
    responses.add(resp)
    assert testClient.post(path, {"name": "testlabel"}).json() == resp_json


@responses.activate
def test_sc_post_not_ok():
    path = "/member"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp = responses.Response(
        method="POST",
        url=url,
        status=422,
    )
    responses.add(resp)
    with pytest.raises(requests.HTTPError):
        testClient.post(path, {"name": "testlabel"})


@responses.activate
def test_sc_put_ok():
    path = "/labels"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp_json = {
        "app_url": "https://app.shortcut.com/test-workspace2/labels/123",
        "archived": True,
        "color": "#6515dd",
        "created_at": "2016-12-31T12:30:00Z",
        "description": "test",
        "entity_type": "label",
        "external_id": None,
        "id": 123,
        "name": "new label name",
        "stats": {
            "num_epics": 123,
            "num_epics_completed": 123,
            "num_epics_in_progress": 123,
            "num_epics_total": 123,
            "num_epics_unstarted": 123,
            "num_points_backlog": 123,
            "num_points_completed": 123,
            "num_points_in_progress": 123,
            "num_points_total": 123,
            "num_points_unstarted": 123,
            "num_related_documents": 123,
            "num_stories_backlog": 123,
            "num_stories_completed": 123,
            "num_stories_in_progress": 123,
            "num_stories_total": 123,
            "num_stories_unestimated": 123,
            "num_stories_unstarted": 123,
        },
        "updated_at": "2016-12-31T12:30:00Z",
    }
    resp = responses.Response(
        method="PUT",
        url=url,
        status=200,
        json=resp_json,
    )
    responses.add(resp)
    assert testClient.put(path, {"name": "new label name"}).json() == resp_json


@responses.activate
def test_sc_put_not_ok():
    path = "/member"
    url = f"https://api.app.shortcut.com/api/v3{path}"
    resp = responses.Response(
        method="PUT",
        url=url,
        status=422,
    )
    responses.add(resp)
    with pytest.raises(requests.HTTPError):
        testClient.put(path)
