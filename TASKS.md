# Codex Task List

## Phase A — Backend Skeleton

- [x] Create FastAPI project
- [x] Add `/health`
- [x] Add `/message`
- [x] Add `.env.example`
- [x] Add Dockerfile
- [x] Add README

## Phase B — Database

- [x] Connect to PostgreSQL
- [x] Implement `save_chat_message(sender_id, role, message)`
- [x] Implement `load_recent_chat(sender_id, limit=20)`
- [x] Implement `load_memory(sender_id)`
- [x] Implement `upsert_memory(sender_id, memory_key, memory_value)`

## Phase C — OpenAI

- [x] Implement memory extraction call
- [x] Parse strict JSON safely
- [x] Implement reply generation call
- [x] Add Filipino/Taglish-friendly system prompt

## Phase D — End-to-End

- [x] `/message` saves user message
- [x] `/message` extracts memory
- [x] `/message` upserts memory
- [x] `/message` loads memory
- [x] `/message` generates reply
- [x] `/message` saves assistant reply
- [x] `/message` returns reply

## Phase E — n8n Simplification

- [ ] Replace SQL/OpenAI n8n nodes with backend HTTP request
- [ ] Keep IF echo filter
- [ ] Keep Facebook Send API node
- [ ] Test Messenger E2E

## Local Verification

- [x] Commit and push backend skeleton
- [x] Configure local OpenAI API key in ignored `.env`
- [x] Start local PostgreSQL with Docker
- [x] Apply database schema
- [x] Verify SQLAlchemy database connection
- [x] Verify OpenAI + PostgreSQL smoke test

## Phase F — Safety

- [x] Never log secrets
- [x] Add basic request validation
- [x] Add max message length
- [x] Add fallback reply if OpenAI fails
- [x] Add scam/OTP safety instruction in system prompt

## Phase G — Messenger Images

- [x] Accept optional image URLs in `/message`
- [x] Forward Messenger image attachment URLs from n8n
- [x] Convert reachable image URLs to data URLs before calling OpenAI
- [x] Keep raw image URLs out of chat history rows
- [x] Add tests for image payload validation and OpenAI image content shape

## Phase H — Family Identity

- [x] Seed initial family member registry
- [x] Add Messenger sender ID linking support
- [x] Include identified family profile in AI context
- [x] Return identified family member metadata from `/message`
- [x] Add scripts to list recent sender IDs and link family members

## Phase I — Messenger Profile Lookup

- [x] Add `messenger_contacts` profile cache
- [x] Accept optional `messenger_profile` in `/message`
- [x] Auto-link exact family name matches
- [x] Personalize non-family contacts with first name only
- [x] Document n8n Meta profile lookup payload
