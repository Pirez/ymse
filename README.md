# ymse

Send transactional email via [Lettermint](https://lettermint.co).

## Install

```bash
uv add ymse
```

## Setup

Create a `.env` file:

```
LETTERMINT_API_TOKEN=your_api_token
LETTERMINT_SENDER=Your Name <you@yourdomain.com>
```

The sender address must be a verified sender in your Lettermint account.

## Usage

```python
from ymse.core import send_email

send_email(
    subject="Hello",
    html_content="<p>Hello world</p>",
    to="recipient@example.com",
)
```

Override the sender for a specific call:

```python
send_email(
    subject="Hello",
    html_content="<p>Hello world</p>",
    to="recipient@example.com",
    sender="Other Name <other@yourdomain.com>",
)
```

## Dev

```bash
just test   # run tests
just lint   # lint
just fmt    # format
just run    # send a test email
```
