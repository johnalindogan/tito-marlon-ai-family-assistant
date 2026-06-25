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
- PostgreSQL container running
- `chat_messages` table exists
- `family_memory` table exists
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
