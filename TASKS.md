# Codex Task List

## Phase A — Backend Skeleton

- [ ] Create FastAPI project
- [ ] Add `/health`
- [ ] Add `/message`
- [ ] Add `.env.example`
- [ ] Add Dockerfile
- [ ] Add README

## Phase B — Database

- [ ] Connect to PostgreSQL
- [ ] Implement `save_chat_message(sender_id, role, message)`
- [ ] Implement `load_recent_chat(sender_id, limit=20)`
- [ ] Implement `load_memory(sender_id)`
- [ ] Implement `upsert_memory(sender_id, memory_key, memory_value)`

## Phase C — OpenAI

- [ ] Implement memory extraction call
- [ ] Parse strict JSON safely
- [ ] Implement reply generation call
- [ ] Add Filipino/Taglish-friendly system prompt

## Phase D — End-to-End

- [ ] `/message` saves user message
- [ ] `/message` extracts memory
- [ ] `/message` upserts memory
- [ ] `/message` loads memory
- [ ] `/message` generates reply
- [ ] `/message` saves assistant reply
- [ ] `/message` returns reply

## Phase E — n8n Simplification

- [ ] Replace SQL/OpenAI n8n nodes with backend HTTP request
- [ ] Keep IF echo filter
- [ ] Keep Facebook Send API node
- [ ] Test Messenger E2E

## Phase F — Safety

- [ ] Never log secrets
- [ ] Add basic request validation
- [ ] Add max message length
- [ ] Add fallback reply if OpenAI fails
- [ ] Add scam/OTP safety instruction in system prompt
