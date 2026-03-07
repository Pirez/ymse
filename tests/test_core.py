from unittest.mock import MagicMock, patch
import pytest
from lettermint.exceptions import ValidationError, TimeoutError
from ymse.core import send_email


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
