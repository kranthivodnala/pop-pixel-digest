# Pop Pixel Digest

A fully automated daily entertainment newsletter delivered to subscribers via email. Every morning it fetches the latest movies, TV shows, OTT releases, game releases, and trailer announcements — builds a styled HTML digest, and sends it through AWS SES.

---

## Features

- **Trailer Announcements** — upcoming movie and TV show trailers from both International and Indian film industries
- **Now In Theaters** — currently playing movies with ratings and genres
- **TV Shows Airing Today** — episodes airing on the current date
- **New on Streaming** — recent releases across Netflix, Amazon Prime Video, Disney+, Apple TV+, Max, Hulu, Disney+ Hotstar, SonyLIV, and Zee5, with the platform name shown on each title
- **New Game Releases** — games released this week with platform info and ratings
- Fully dark-themed HTML email with hero cards, genre pills, and rating bars
- Serverless subscriber management via AWS DynamoDB
- Scheduled daily at 9 AM UTC via GitHub Actions (zero servers)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Email delivery | AWS SES (`send_raw_email`) |
| Subscriber store | AWS DynamoDB (on-demand / serverless) |
| Scheduler | GitHub Actions cron |
| Template engine | Jinja2 |
| Movie & TV data | [TMDB API](https://www.themoviedb.org/) |
| Games data | [RAWG API](https://rawg.io/) |

---

## Architecture

```
GitHub Actions (cron 9 AM UTC)
        │
        ▼
    main.py
        │
        ├── fetch_trailers()    ── TMDB /movie/upcoming + /tv/on_the_air (US + IN regions)
        ├── fetch_movies()      ── TMDB /movie/now_playing
        ├── fetch_tv_shows()    ── TMDB /tv/airing_today
        ├── fetch_ott_releases()── TMDB /discover/movie per provider (US + IN)
        └── fetch_games()       ── RAWG /games (past 7 days)
                │
                ▼
        build_digest()          ── Jinja2 HTML template
                │
                ▼
        get_all_subscribers()   ── DynamoDB scan
                │
                ▼
        send_digest()           ── AWS SES send_raw_email
                                   (multipart/alternative + List-Unsubscribe header)
```

---

## Project Structure

```
pop-pixel-digest/
├── main.py                          # Orchestrates fetch → build → send
├── requirements.txt
├── .env.example
├── src/
│   ├── fetchers/
│   │   ├── trailers.py              # TMDB trailer announcements (US + IN)
│   │   ├── movies.py                # TMDB now-playing movies
│   │   ├── tv_shows.py              # TMDB TV shows airing today
│   │   ├── ott.py                   # TMDB OTT releases per provider
│   │   ├── games.py                 # RAWG weekly game releases
│   │   └── genre_map.py             # TMDB genre ID → name mapping
│   ├── digest_builder.py            # Renders Jinja2 HTML template
│   ├── email_sender.py              # AWS SES with spam-prevention headers
│   └── subscriber_manager.py        # DynamoDB CRUD with pagination
├── templates/
│   └── digest.html                  # Dark-themed newsletter template
├── scripts/
│   ├── subscribe.py                 # Add a subscriber to DynamoDB
│   ├── unsubscribe.py               # Soft-delete a subscriber
│   └── setup_dynamodb.py            # Create the DynamoDB table (run once)
└── .github/
    └── workflows/
        └── daily_digest.yml         # GitHub Actions cron schedule
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/kranthivodnala/pop-pixel-digest.git
cd pop-pixel-digest
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env`:

```
TMDB_API_KEY=            # https://www.themoviedb.org/settings/api
RAWG_API_KEY=            # https://rawg.io/apidocs
AWS_ACCESS_KEY_ID=       # IAM user with SES + DynamoDB permissions
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
SES_SENDER_EMAIL=        # Must be verified in AWS SES
DYNAMODB_TABLE=pop-pixel-digest-subscribers
```

### 3. Create the DynamoDB table

```bash
python scripts/setup_dynamodb.py
```

### 4. Verify sender email in AWS SES

Go to **AWS Console → SES → Verified identities → Create identity** and verify your sender email address.

> For production sending (not just sandbox), request production access under **SES → Account dashboard**.

### 5. Add subscribers

```bash
python scripts/subscribe.py you@example.com
```

### 6. Test locally

```bash
python main.py
```

---

## GitHub Actions — Automated Daily Delivery

Add the following secrets to your repo under **Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `TMDB_API_KEY` | TMDB API key |
| `RAWG_API_KEY` | RAWG API key |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_REGION` | e.g. `us-east-1` |
| `SES_SENDER_EMAIL` | Verified sender address |
| `DYNAMODB_TABLE` | e.g. `pop-pixel-digest-subscribers` |

The workflow runs automatically every day at **9:00 AM UTC**. You can also trigger it manually from **Actions → Daily Pop Pixel Digest → Run workflow**.

---

## Subscriber Management

```bash
# Add a subscriber
python scripts/subscribe.py user@example.com

# Remove a subscriber
python scripts/unsubscribe.py user@example.com
```

Subscribers are stored in DynamoDB with `email`, `subscribed_at`, and `is_active` fields. Unsubscribing performs a soft delete (`is_active = false`) rather than removing the record.

---

## IAM Permissions Required

```json
{
  "Effect": "Allow",
  "Action": ["ses:SendRawEmail"],
  "Resource": "*"
},
{
  "Effect": "Allow",
  "Action": ["dynamodb:Scan", "dynamodb:PutItem", "dynamodb:UpdateItem"],
  "Resource": "arn:aws:dynamodb:*:*:table/pop-pixel-digest-subscribers"
}
```

---

## Data Sources

- **TMDB** — movies, TV shows, OTT releases, trailer videos. Free tier: 40 requests/10 seconds.
- **RAWG** — game releases and ratings. Free tier: 20,000 requests/month.

> This product uses the TMDB API but is not endorsed or certified by TMDB.
