from unittest.mock import MagicMock, patch
import pytest
from lettermint.exceptions import (
    ClientError,
    HttpRequestError,
    TimeoutError,
    ValidationError,
)
from ymse.core import run, send_email


@pytest.fixture
def mock_client(monkeypatch):
    monkeypatch.setenv("LETTERMINT_API_TOKEN", "test-token")
    client = MagicMock()
    chain = client.email.from_.return_value
    chain.to.return_value = chain
    chain.subject.return_value = chain
    chain.html.return_value = chain
    chain.send.return_value = {"message_id": "abc123"}
    with patch("ymse.core.Lettermint", return_value=client):
        yield chain


def test_send_email_success(mock_client):
    send_email("Subject", "<p>Hello</p>", "to@example.com", "From <from@example.com>")
    mock_client.send.assert_called_once()


def test_send_email_validation_error(mock_client):
    mock_client.send.side_effect = ValidationError("invalid", "invalid_parameter")
    with pytest.raises(ValidationError):
        send_email(
            "Subject", "<p>Hello</p>", "to@example.com", "From <from@example.com>"
        )


def test_send_email_timeout(mock_client):
    mock_client.send.side_effect = TimeoutError("timed out")
    with pytest.raises(TimeoutError):
        send_email(
            "Subject", "<p>Hello</p>", "to@example.com", "From <from@example.com>"
        )


def test_send_email_missing_token(monkeypatch):
    monkeypatch.delenv("LETTERMINT_API_TOKEN", raising=False)
    with pytest.raises(KeyError):
        send_email(
            "Subject", "<p>Hello</p>", "to@example.com", "From <from@example.com>"
        )


def test_send_email_client_error(mock_client):
    mock_client.send.side_effect = ClientError("bad request")
    with pytest.raises(ClientError):
        send_email(
            "Subject", "<p>Hello</p>", "to@example.com", "From <from@example.com>"
        )


def test_send_email_http_error(mock_client):
    mock_client.send.side_effect = HttpRequestError("server error", 500)
    with pytest.raises(HttpRequestError):
        send_email(
            "Subject", "<p>Hello</p>", "to@example.com", "From <from@example.com>"
        )


def test_send_email_default_sender(mock_client, monkeypatch):
    monkeypatch.setenv("LETTERMINT_SENDER", "Env <env@example.com>")
    send_email("Subject", "<p>Hello</p>", "to@example.com")
    mock_client.send.assert_called_once()


def test_run_sends_email():
    with patch("ymse.core.send_email") as mock_send:
        run()
    mock_send.assert_called_once()
