# Prompt for Codex

You are helping build the backend for **Tito Marlon Family AI Assistant**.

## Context

Tito Marlon is a private Facebook Messenger AI assistant for the Alindogan family. It is used mainly by family members, including senior citizens. The bot should speak in simple English, Filipino, or natural Taglish depending on the user's language.

The current Messenger/n8n infrastructure is already working, but memory logic is difficult to maintain in n8n. We want to move the core logic into a FastAPI backend.

## Build Request

Create a production-ready but simple **Python FastAPI backend** with PostgreSQL and OpenAI integration.

## Required Endpoint

### `POST /message`

Request body:

```json
{
  "sender_id": "string",
  "message": "string"
}
```

Response body:

```json
{
  "reply": "string",
  "memories_saved": [
    {
      "memory_key": "string",
      "memory_value": "string"
    }
  ]
}
```

## Required Behavior

When `/message` receives a message:

1. Validate input.
2. Save the user message into `chat_messages`.
3. Load permanent memory for that `sender_id` from `family_memory`.
4. Load recent chat history from `chat_messages`.
5. Use OpenAI to extract any new permanent memory from the user message.
6. If new memory is found, upsert it into `family_memory`.
7. Use OpenAI to generate a friendly Tito Marlon reply using:
   - Permanent memory
   - Recent chat history
   - User message
8. Save assistant reply into `chat_messages`.
9. Return the reply and any memories saved.

## Database Tables

Use these existing tables:

```sql
CREATE TABLE chat_messages (
  id BIGSERIAL PRIMARY KEY,
  sender_id TEXT NOT NULL,
  role TEXT NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_chat_messages_sender_created
ON chat_messages(sender_id, created_at DESC);

CREATE TABLE family_memory (
  id BIGSERIAL PRIMARY KEY,
  sender_id TEXT NOT NULL,
  memory_key TEXT NOT NULL,
  memory_value TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(sender_id, memory_key)
);
```

## Memory Extraction

Use a separate OpenAI call to extract permanent memories.

The extraction prompt should return strict JSON only:

If no memory:

```json
{"save": false}
```

If memory exists:

```json
{
  "save": true,
  "memory_key": "favorite_food",
  "memory_value": "Sinigang"
}
```

Support examples:

- "My favorite food is sinigang" → `favorite_food = Sinigang`
- "Paborito kong pagkain ang tahong" → `favorite_food = tahong`
- "My pet is Baby William" → `pet_name = Baby William`
- "Ang pet ko ay si Baby William" → `pet_name = Baby William`
- "I am wearing a white polo shirt" → `current_clothing = white polo shirt`
- "My mother's birthday is October 13" → `mother_birthday = October 13`
- "Koko's birthday is May 12" → `koko_birthday = May 12`

Use snake_case memory keys.

## Assistant Personality

System prompt should define Tito Marlon as:

```text
You are Tito Marlon, the Alindogan Family AI Assistant.

You are warm, respectful, patient, and family-oriented.

You help family members with:
- family information
- birthdays
- reminders
- technology questions
- scam and OTP safety
- everyday questions

Use simple English, Filipino, or natural Taglish depending on the user's language.

If permanent memory contains the answer, answer confidently.
If the memory does not contain the answer, say you do not know yet and ask the user to tell you.

You are not the real Tito Marlon. You are his AI assistant helping the family.
```

## Echo Loop Prevention

The backend does not need to handle Facebook Messenger echo loops. n8n should filter `is_echo=true` before calling this backend.

## Required Files

Please create:

```text
app/
  main.py
  config.py
  db.py
  models.py
  memory.py
  ai.py
  schemas.py
requirements.txt
Dockerfile
docker-compose.yml
.env.example
README.md
```

## Technical Requirements

- Use FastAPI.
- Use async if practical, but simple sync SQLAlchemy is acceptable.
- Use SQLAlchemy or psycopg.
- Use OpenAI Python SDK.
- Use Pydantic models.
- Include good error handling.
- Include structured logs.
- Include `/health` endpoint.
- Include unit-testable functions for memory extraction and prompt construction.
- Never log secrets.
- Never expose API keys in responses.

## Expected Local Environment

Existing PostgreSQL container:

```text
Host from another Docker container: host.docker.internal
Port: 5432
Database: titomarlon
User: titomarlon
Password: stored locally by user
```

`.env.example`:

```env
OPENAI_API_KEY=
DATABASE_URL=postgresql+psycopg://titomarlon:CHANGE_ME@host.docker.internal:5432/titomarlon
OPENAI_MODEL=gpt-4.1-mini
APP_ENV=development
LOG_LEVEL=INFO
```

## Definition of Done

A local test should work:

```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"sender_id":"test-user","message":"Paborito kong pagkain ang Sinigang"}'
```

Expected response should mention Sinigang or acknowledge saving the memory.

Then:

```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"sender_id":"test-user","message":"Ano ang paborito kong pagkain?"}'
```

Expected response should answer that favorite food is Sinigang.
