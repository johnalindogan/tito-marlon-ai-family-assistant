# Tito Marlon Family AI Assistant — Codex Handoff Package

## Project Goal

Build **Tito Marlon**, a private family AI assistant for the Alindogan family, primarily used through **Facebook Messenger**. The bot is intended for senior-friendly family assistance: reminders, family facts, scam/OTP safety guidance, emergency escalation, and simple Taglish Q&A.

## Current Working Status

The following are already working:

- Facebook Page: **Tito Marlon**
- Meta Developer App: **Tito Marlon AI Assistant**
- Messenger product enabled
- Messenger webhook verified
- Facebook Page Access Token generated
- Cloudflare Tunnel working
- n8n self-hosted and publicly reachable at:
  - `https://titomarlon.alindogan.com`
- Messenger → Meta → Cloudflare → n8n webhook working
- n8n → OpenAI working
- n8n → Facebook Graph Send API working
- n8n → backend image URL forwarding working for Messenger image attachments
- PostgreSQL container running
- `chat_messages` table exists
- `family_memory` table exists
- `family_members` table exists with initial Alindogan family member profiles
- `messenger_contacts` table exists for cached Meta profile lookup results
- Permanent memory can be manually inserted and read

## Current Pain Point

The n8n workflow became difficult to maintain due to:

- Echo-loop prevention complexity
- Multiple SQL nodes
- Memory extraction/upsert logic
- Need for reliable permanent memory
- Hard-to-debug expression paths between nodes
- OpenAI output shape handling

## Recommended Refactor

Move the core intelligence and memory logic into a backend service, and keep n8n only as the routing/orchestration layer.

Target architecture:

```text
Facebook Messenger
        ↓
Meta Webhook
        ↓
Cloudflare Tunnel
        ↓
n8n Webhook
        ↓
Tito Marlon Backend API
        ↓
PostgreSQL + OpenAI
        ↓
n8n
        ↓
Facebook Graph API Send Message
        ↓
Messenger Reply
```

The backend should expose:

```http
POST /message
```

Input:

```json
{
  "sender_id": "messenger_sender_id",
  "message": "user message text"
}
```

Output:

```json
{
  "reply": "assistant reply text",
  "memories_saved": [
    {
      "memory_key": "favorite_food",
      "memory_value": "Sinigang"
    }
  ]
}
```

## Suggested Backend Stack

Preferred: **Python FastAPI**

Rationale:
- Easy to debug
- Good PostgreSQL support
- Good OpenAI SDK support
- Easy Dockerization
- Simple endpoint integration from n8n

Alternative: Node.js / TypeScript Express.

## Important Security Notes

Do not commit secrets.

Use `.env` for:

- `OPENAI_API_KEY`
- `DATABASE_URL`
- `APP_ENV`
- `LOG_LEVEL`

Do not store:
- Facebook Page Access Token in GitHub
- OpenAI API key in code
- PostgreSQL password in code

## Development Target

Make the backend run locally first:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then call it from n8n:

```text
http://host.docker.internal:8000/message
```

Later optionally expose via Cloudflare only if needed.

## Backend Quick Start

Create a local environment file:

```bash
copy .env.example .env
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start local PostgreSQL:

```bash
python scripts/setup_local_env.py
docker compose -f docker-compose.postgres.yml up -d
docker cp DATABASE_SCHEMA.sql titomarlon-postgres:/tmp/DATABASE_SCHEMA.sql
docker exec titomarlon-postgres psql -U titomarlon -d titomarlon -f /tmp/DATABASE_SCHEMA.sql
python scripts/reset_local_postgres_password.py
python scripts/database_smoke_test.py
```

Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check health:

```bash
curl http://localhost:8000/health
```

Send a test message:

```bash
python scripts/smoke_test.py
```

Run an explicit OpenAI-backed smoke test:

```bash
python scripts/openai_smoke_test.py
```

Current backend status:

- `/health` is available.
- `/message` validates requests.
- `/message` accepts text, up to 3 image URLs, or both.
- `/message` saves user and assistant chat rows when `DATABASE_URL` is configured and the schema exists.
- `/message` extracts memories and generates replies with OpenAI when `OPENAI_API_KEY` is configured.
- `/message` can download image URLs and pass them to OpenAI for visual understanding.
- `/message` caches Messenger profile lookup data, auto-links exact family name matches, and customizes replies with the family preferred name or contact first name.
- `/message` returns a safe fallback reply when OpenAI is not configured or fails.

## Family Member Identity

Messenger sends a page-scoped `sender_id`, not the public Facebook profile URL. n8n should look up the sender's Messenger profile through Meta and pass it to `/message` as `messenger_profile`.

When the profile's normalized `first_name + last_name` exactly matches a seeded `family_members.full_name`, the backend auto-links that sender to the family member. Non-family friends are cached in `messenger_contacts` and Tito Marlon may use their first name without assigning a family role.

List recent Messenger sender IDs:

```bash
python scripts/list_recent_senders.py
```

Link a sender ID to a family profile:

```bash
python scripts/link_family_member.py nelon_alindogan <MESSENGER_SENDER_ID>
```

Manual linking is only needed if Meta's profile name does not exactly match the seeded family member name.

Seeded `member_key` values:

- `nelon_alindogan`
- `corazon_alindogan`
- `mary_grace_alindogan`
- `joseph_noel_alindogan`
- `james_nelson_alindogan`

Local PostgreSQL uses host port `55432` to avoid conflicts with other Postgres installations on the default `5432` port.
