import httpx

from researchflow.http import HTTPClient


def make_response(
    status_code: int,
    *,
    json_data: dict | None = None,
) -> httpx.Response:
    """Create an HTTPX response with an associated request."""

    request = httpx.Request(
        "GET",
        "https://example.com",
    )

    return httpx.Response(
        status_code,
        json=json_data,
        request=request,
    )


def test_http_client_success(monkeypatch):
    response = make_response(
        200,
        json_data={"status": "ok"},
    )

    def mock_get(self, *args, **kwargs):
        return response

    monkeypatch.setattr(
        httpx.Client,
        "get",
        mock_get,
    )

    client = HTTPClient()

    result = client.get(
        "https://example.com"
    )

    assert result.status_code == 200
    assert result.json() == {
        "status": "ok"
    }


def test_http_client_retries_rate_limit(
    monkeypatch,
):
    responses = [
        make_response(429),
        make_response(
            200,
            json_data={"status": "ok"},
        ),
    ]

    calls = []

    def mock_get(self, *args, **kwargs):
        calls.append(1)
        return responses.pop(0)

    monkeypatch.setattr(
        httpx.Client,
        "get",
        mock_get,
    )

    monkeypatch.setattr(
        "researchflow.http.client.time.sleep",
        lambda _: None,
    )

    client = HTTPClient(
        max_retries=2,
    )

    result = client.get(
        "https://example.com"
    )

    assert result.status_code == 200
    assert result.json() == {
        "status": "ok"
    }
    assert len(calls) == 2