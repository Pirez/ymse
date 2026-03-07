# ymse

[![PyPI](https://img.shields.io/pypi/v/ymse)](https://pypi.org/project/ymse/)
[![Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen)](https://github.com/Pirez/ymse)

Misc utilities: transactional email via [Lettermint](https://lettermint.co) and Doffin procurement search.

## Install

```bash
uv add ymse
```

## Email

### Setup

Create a `.env` file:

```
LETTERMINT_API_TOKEN=your_api_token
LETTERMINT_SENDER=Your Name <you@yourdomain.com>
```

The sender address must be a verified sender in your Lettermint account.

### Usage

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

## Doffin

Search Norwegian public procurement notices ([doffin.no](https://doffin.no)).

### Setup

```
DOFFIN_API_KEY=your_subscription_key
```

### Usage

```python
from ymse import search_doffin

notices = search_doffin("IT-tjenester", days=7)
# or multiple queries
notices = search_doffin(["IT-tjenester", "renholdsutstyr"], days=30)
```

Each result dict contains: `id`, `title`, `description`, `buyer`, `type`, `published`, `value`, `currency`, `url`, `query`.

## Dev

```bash
just test   # run tests
just lint   # lint
just fmt    # format
just run    # send a test email
```
