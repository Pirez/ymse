"""Transactional email via Lettermint."""

import os
from lettermint import Lettermint
from lettermint.exceptions import (
    ValidationError,
    ClientError,
    TimeoutError,
    HttpRequestError,
)
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def send_email(
    subject: str,
    html_content: str,
    to: str,
    sender: str | None = None,
) -> None:
    """Send an HTML email via Lettermint.

    Args:
        subject: Email subject line.
        html_content: HTML body.
        to: Recipient address.
        sender: Verified sender; defaults to the LETTERMINT_SENDER env var.

    Raises:
        KeyError: If LETTERMINT_API_TOKEN (or LETTERMINT_SENDER when no sender is
            given) is not set.
        ValidationError: On a 422 response.
        ClientError: On a 400 response.
        TimeoutError: If the request times out.
        HttpRequestError: On any other HTTP error.
    """
    sender = sender or os.environ["LETTERMINT_SENDER"]
    client = Lettermint(api_token=os.environ["LETTERMINT_API_TOKEN"])

    logger.info("Sending email to <cyan>{}</> — subject: <cyan>{}</>", to, subject)

    try:
        response = (
            client.email.from_(sender).to(to).subject(subject).html(html_content).send()
        )
        logger.success("Email sent | ID: <green>{}</>", response["message_id"])
    except ValidationError as e:
        logger.error("Validation error: {}", e.error_type)
        raise
    except ClientError as e:
        logger.error("Client error: {}", e)
        raise
    except TimeoutError as e:
        logger.error("Timeout: {}", e)
        raise
    except HttpRequestError as e:
        logger.error("HTTP error {}: {}", e.status_code, e)
        raise


def run() -> None:
    """Send a hardcoded test email to verify the Lettermint setup."""
    send_email(
        subject="Testing automated email sending with Lettermint",
        html_content="Functionality is working! This email was sent using the Lettermint SDK.",
        to="x@icloud.com",
    )
