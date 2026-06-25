-- Tito Marlon PostgreSQL Schema

CREATE TABLE IF NOT EXISTS chat_messages (
  id BIGSERIAL PRIMARY KEY,
  sender_id TEXT NOT NULL,
  role TEXT NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_sender_created
ON chat_messages(sender_id, created_at DESC);

CREATE TABLE IF NOT EXISTS family_memory (
  id BIGSERIAL PRIMARY KEY,
  sender_id TEXT NOT NULL,
  memory_key TEXT NOT NULL,
  memory_value TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(sender_id, memory_key)
);

-- Optional seed examples. Replace sender_id before use.
INSERT INTO family_memory (sender_id, memory_key, memory_value)
VALUES
('<MESSENGER_SENDER_ID>', 'favorite_food', 'Sinigang'),
('<MESSENGER_SENDER_ID>', 'pet_name', 'Baby William'),
('<MESSENGER_SENDER_ID>', 'current_clothing', 'white polo shirt')
ON CONFLICT (sender_id, memory_key)
DO UPDATE SET memory_value = EXCLUDED.memory_value, updated_at = now();
