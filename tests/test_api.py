import requests
import polisprojekt.data.api_fetch as api_fetch

def test_fetch_events_network_error(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr(api_fetch.requests, "get", boom)

    assert api_fetch.fetch_events(retries=1) is None

class DummyResp500:
    def raise_for_status(self):
        raise requests.HTTPError("500")

def test_fetch_events_http_error(monkeypatch):
    def fake_get(*args, **kwargs):
        return DummyResp500()

    monkeypatch.setattr("polisprojekt.data.api_fetch.requests.get", fake_get)
    assert api_fetch.fetch_events(retries=1) is None

class DummyResp200:
    status_code = 200
    def raise_for_status(self):
        return None
    def json(self):
        return {"oops": "not a list"}

def test_fetch_events_faulty_json_returns(monkeypatch):
    def fake_get(*args, **kwargs):
        return DummyResp200()

    monkeypatch.setattr("polisprojekt.data.api_fetch.requests.get", fake_get)
    assert api_fetch.fetch_events() is None

class DummyRespEmpty:
    def raise_for_status(self):
        return None  # inget HTTP-fel

    def json(self):
        return []  # tom lista


def test_fetch_events_handles_empty_list(monkeypatch):
    def fake_get(*args, **kwargs):
        return DummyRespEmpty()

    monkeypatch.setattr("polisprojekt.data.api_fetch.requests.get", fake_get)

    assert api_fetch.fetch_events() is None

class DummyRespBadJSON:
    def raise_for_status(self):
        return None  # inget HTTP-fel

    def json(self):
        raise ValueError("not json")


def test_fetch_events_bad_json(monkeypatch):
    def fake_get(*args, **kwargs):
        return DummyRespBadJSON()

    monkeypatch.setattr("polisprojekt.data.api_fetch.requests.get", fake_get)

    assert api_fetch.fetch_events(retries=1) is None