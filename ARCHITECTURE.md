# Architecture

## Current Infrastructure

```text
Facebook Messenger
  ↓
Tito Marlon Facebook Page
  ↓
Meta Messenger Webhook
  ↓
Cloudflare Tunnel
  ↓
n8n at https://titomarlon.alindogan.com
  ↓
OpenAI + PostgreSQL + Facebook Graph API
```

## Proposed Refactored Architecture

```text
Messenger user
  ↓
Facebook Page / Meta
  ↓
Meta Webhook
  ↓
Cloudflare Tunnel
  ↓
n8n Webhook
  ↓
Tito Marlon Backend API
      ├── PostgreSQL: chat_messages
      ├── PostgreSQL: family_memory
      └── OpenAI
  ↓
n8n
  ↓
Facebook Graph API /me/messages
  ↓
Messenger reply
```

## n8n Responsibility After Refactor

n8n should only:

1. Receive Messenger webhook POST.
2. Filter out echo messages where `message.is_echo == true`.
3. Extract:
   - `sender_id`
   - `message.text`
4. POST to backend `/message`.
5. Send backend reply through Facebook Graph API.
6. Return HTTP 200 to Meta.

## Backend Responsibility

Backend should own:

- Chat history persistence
- Permanent memory extraction
- Memory upsert
- Recent memory retrieval
- Prompt construction
- OpenAI reply generation
- Assistant reply persistence
