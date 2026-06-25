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

CREATE TABLE IF NOT EXISTS family_members (
  member_key TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  preferred_name TEXT NOT NULL,
  relationship_label TEXT NOT NULL,
  aliases_json TEXT NOT NULL DEFAULT '[]',
  facebook_url TEXT NOT NULL,
  messenger_sender_id TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO family_members (
  member_key,
  full_name,
  preferred_name,
  relationship_label,
  aliases_json,
  facebook_url
)
VALUES
('nelon_alindogan', 'Nelon Alindogan', 'Papa Nelon', 'Papa Nelon / Grandpa Nelon', '["Papa Nelon", "Grandpa Nelon", "Granpa Nelon", "Nelon"]', 'https://www.facebook.com/leaderalindogan'),
('corazon_alindogan', 'Corazon Alindogan', 'Mama Cora', 'Mama Cora / Grandma Cora', '["Mama Cora", "Grandma Cora", "Granma Cora", "Cora", "Corazon"]', 'https://www.facebook.com/cora.alindogan'),
('mary_grace_alindogan', 'Mary Grace Alindogan', 'Ate Grace', 'Grace / Ate Grace / Tita Grace', '["Grace", "Ate Grace", "Tita Grace", "Mary Grace"]', 'https://www.facebook.com/mgalindogan'),
('joseph_noel_alindogan', 'Joseph Noel Alindogan', 'Kuya Joseph', 'Joseph / Kuya Joseph / Tito Joseph', '["Joseph", "Kuya Joseph", "Tito Joseph", "Joseph Noel"]', 'https://www.facebook.com/joseph.alindogan.7'),
('james_nelson_alindogan', 'James Nelson Alindogan', 'Tito James', 'James / Emson / Tito James', '["James", "Emson", "Tito James", "James Nelson"]', 'https://www.facebook.com/DogsNaDiAso')
ON CONFLICT (member_key)
DO UPDATE SET
  full_name = EXCLUDED.full_name,
  preferred_name = EXCLUDED.preferred_name,
  relationship_label = EXCLUDED.relationship_label,
  aliases_json = EXCLUDED.aliases_json,
  facebook_url = EXCLUDED.facebook_url,
  updated_at = now();

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

CREATE TABLE IF NOT EXISTS messenger_contacts (
  sender_id TEXT PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  profile_pic TEXT,
  locale TEXT,
  timezone INTEGER,
  family_member_key TEXT REFERENCES family_members(member_key),
  first_seen_at TIMESTAMPTZ DEFAULT now(),
  last_seen_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
