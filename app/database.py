from collections.abc import Generator
from contextlib import contextmanager
import json
import re

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def create_db_engine() -> Engine | None:
    settings = get_settings()
    if not settings.database_url:
        return None
    return create_engine(settings.database_url, pool_pre_ping=True)


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None


@contextmanager
def session_scope() -> Generator[Session | None, None, None]:
    if SessionLocal is None:
        yield None
        return

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def save_chat_message(session: Session, sender_id: str, role: str, message: str) -> None:
    session.execute(
        text(
            """
            INSERT INTO chat_messages (sender_id, role, message)
            VALUES (:sender_id, :role, :message)
            """
        ),
        {"sender_id": sender_id, "role": role, "message": message},
    )


def load_recent_chat(session: Session, sender_id: str, limit: int = 20) -> list[dict[str, str]]:
    rows = session.execute(
        text(
            """
            SELECT role, message
            FROM chat_messages
            WHERE sender_id = :sender_id
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        {"sender_id": sender_id, "limit": limit},
    ).mappings()

    return [{"role": row["role"], "message": row["message"]} for row in reversed(list(rows))]


def load_memory(session: Session, sender_id: str) -> dict[str, str]:
    rows = session.execute(
        text(
            """
            SELECT memory_key, memory_value
            FROM family_memory
            WHERE sender_id = :sender_id
            ORDER BY memory_key ASC
            """
        ),
        {"sender_id": sender_id},
    ).mappings()

    return {row["memory_key"]: row["memory_value"] for row in rows}


def load_family_member_by_sender_id(session: Session, sender_id: str) -> dict[str, object] | None:
    row = session.execute(
        text(
            """
            SELECT member_key, full_name, preferred_name, relationship_label, aliases_json, facebook_url
            FROM family_members
            WHERE messenger_sender_id = :sender_id
            """
        ),
        {"sender_id": sender_id},
    ).mappings().first()

    if row is None:
        return None

    return {
        "member_key": row["member_key"],
        "full_name": row["full_name"],
        "preferred_name": row["preferred_name"],
        "relationship_label": row["relationship_label"],
        "aliases": json.loads(row["aliases_json"]),
        "facebook_url": row["facebook_url"],
    }


def load_family_member_by_key(session: Session, member_key: str) -> dict[str, object] | None:
    row = session.execute(
        text(
            """
            SELECT member_key, full_name, preferred_name, relationship_label, aliases_json, facebook_url
            FROM family_members
            WHERE member_key = :member_key
            """
        ),
        {"member_key": member_key},
    ).mappings().first()

    if row is None:
        return None

    return {
        "member_key": row["member_key"],
        "full_name": row["full_name"],
        "preferred_name": row["preferred_name"],
        "relationship_label": row["relationship_label"],
        "aliases": json.loads(row["aliases_json"]),
        "facebook_url": row["facebook_url"],
    }


def load_messenger_contact(session: Session, sender_id: str) -> dict[str, object] | None:
    row = session.execute(
        text(
            """
            SELECT sender_id, first_name, last_name, profile_pic, locale, timezone, family_member_key
            FROM messenger_contacts
            WHERE sender_id = :sender_id
            """
        ),
        {"sender_id": sender_id},
    ).mappings().first()

    if row is None:
        return None

    return {
        "sender_id": row["sender_id"],
        "first_name": row["first_name"] or "",
        "last_name": row["last_name"] or "",
        "profile_pic": row["profile_pic"] or "",
        "locale": row["locale"] or "",
        "timezone": row["timezone"],
        "family_member_key": row["family_member_key"],
    }


def upsert_messenger_contact(
    session: Session,
    sender_id: str,
    profile: dict[str, object],
) -> dict[str, object]:
    first_name = str(profile.get("first_name") or "").strip()
    last_name = str(profile.get("last_name") or "").strip()
    profile_pic = str(profile.get("profile_pic") or "").strip()
    locale = str(profile.get("locale") or "").strip()
    timezone = profile.get("timezone")
    family_member_key = find_family_member_key_by_full_name(session, first_name, last_name)

    session.execute(
        text(
            """
            INSERT INTO messenger_contacts (
              sender_id,
              first_name,
              last_name,
              profile_pic,
              locale,
              timezone,
              family_member_key,
              first_seen_at,
              last_seen_at,
              updated_at
            )
            VALUES (
              :sender_id,
              :first_name,
              :last_name,
              :profile_pic,
              :locale,
              :timezone,
              :family_member_key,
              now(),
              now(),
              now()
            )
            ON CONFLICT (sender_id)
            DO UPDATE SET
              first_name = EXCLUDED.first_name,
              last_name = EXCLUDED.last_name,
              profile_pic = EXCLUDED.profile_pic,
              locale = EXCLUDED.locale,
              timezone = EXCLUDED.timezone,
              family_member_key = EXCLUDED.family_member_key,
              last_seen_at = now(),
              updated_at = now()
            """
        ),
        {
            "sender_id": sender_id,
            "first_name": first_name,
            "last_name": last_name,
            "profile_pic": profile_pic,
            "locale": locale,
            "timezone": timezone,
            "family_member_key": family_member_key,
        },
    )

    if family_member_key:
        link_family_member_sender(session, family_member_key, sender_id)

    return {
        "sender_id": sender_id,
        "first_name": first_name,
        "last_name": last_name,
        "profile_pic": profile_pic,
        "locale": locale,
        "timezone": timezone,
        "family_member_key": family_member_key,
    }


def find_family_member_key_by_full_name(
    session: Session,
    first_name: str,
    last_name: str,
) -> str | None:
    normalized_profile_name = _normalize_name(f"{first_name} {last_name}")
    if not normalized_profile_name:
        return None

    rows = session.execute(
        text("SELECT member_key, full_name FROM family_members")
    ).mappings()
    matches = [
        row["member_key"]
        for row in rows
        if _normalize_name(row["full_name"]) == normalized_profile_name
    ]

    return matches[0] if len(matches) == 1 else None


def _normalize_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def link_family_member_sender(session: Session, member_key: str, sender_id: str) -> None:
    session.execute(
        text(
            """
            UPDATE family_members
            SET messenger_sender_id = :sender_id, updated_at = now()
            WHERE member_key = :member_key
            """
        ),
        {"member_key": member_key, "sender_id": sender_id},
    )
    session.execute(
        text(
            """
            UPDATE messenger_contacts
            SET family_member_key = :member_key, updated_at = now()
            WHERE sender_id = :sender_id
            """
        ),
        {"member_key": member_key, "sender_id": sender_id},
    )


def upsert_memory(session: Session, sender_id: str, memory_key: str, memory_value: str) -> None:
    session.execute(
        text(
            """
            INSERT INTO family_memory (sender_id, memory_key, memory_value)
            VALUES (:sender_id, :memory_key, :memory_value)
            ON CONFLICT (sender_id, memory_key)
            DO UPDATE SET memory_value = EXCLUDED.memory_value, updated_at = now()
            """
        ),
        {
            "sender_id": sender_id,
            "memory_key": memory_key,
            "memory_value": memory_value,
        },
    )
