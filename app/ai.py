import base64
import json
import logging
from functools import lru_cache
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from openai import OpenAI

from app.config import get_settings
from app.prompts import FALLBACK_REPLY, MEMORY_EXTRACTION_PROMPT, SYSTEM_PROMPT, format_memory
from app.schemas import MemorySaved

logger = logging.getLogger(__name__)
MAX_IMAGE_BYTES = 7_000_000


@lru_cache
def get_openai_client() -> OpenAI | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def extract_memories(message: str) -> list[MemorySaved]:
    client = get_openai_client()
    if client is None:
        return []

    settings = get_settings()
    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": MEMORY_EXTRACTION_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content or '{"memories":[]}'
        parsed = json.loads(content)
        return _parse_memories(parsed)
    except Exception:
        logger.exception("Memory extraction failed")
        return []


def generate_reply(
    sender_id: str,
    message: str,
    image_urls: list[str],
    family_member: dict[str, object] | None,
    messenger_contact: dict[str, object] | None,
    recent_chat: list[dict[str, str]],
    memory: dict[str, str],
) -> str:
    client = get_openai_client()
    if client is None:
        return FALLBACK_REPLY

    settings = get_settings()
    context = (
        f"Messenger sender_id: {sender_id}\n\n"
        f"Identified family member:\n{_format_family_member(family_member)}\n\n"
        f"Messenger contact:\n{_format_messenger_contact(messenger_contact)}\n\n"
        f"Saved family memory:\n{format_memory(memory)}"
    )

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": context},
    ]
    messages.extend(_chat_history_messages(recent_chat))
    messages.append({"role": "user", "content": _user_content(message, image_urls)})

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.4,
        )
        reply = (response.choices[0].message.content or "").strip()
        return reply or FALLBACK_REPLY
    except Exception as exc:
        logger.error("Reply generation failed: %s", exc.__class__.__name__)
        return FALLBACK_REPLY


def _parse_memories(parsed: Any) -> list[MemorySaved]:
    raw_memories = parsed.get("memories", []) if isinstance(parsed, dict) else []
    if not isinstance(raw_memories, list):
        return []

    memories: list[MemorySaved] = []
    for item in raw_memories:
        if not isinstance(item, dict):
            continue
        key = _clean_memory_text(item.get("memory_key", ""), max_length=80)
        value = _clean_memory_text(item.get("memory_value", ""), max_length=500)
        if key and value:
            memories.append(MemorySaved(memory_key=key, memory_value=value))
    return memories[:10]


def _clean_memory_text(value: Any, max_length: int) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]


def _chat_history_messages(recent_chat: list[dict[str, str]]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for row in recent_chat:
        role = row.get("role")
        if role not in {"user", "assistant"}:
            continue
        content = row.get("message", "").strip()
        if content:
            messages.append({"role": role, "content": content})
    return messages[-20:]


def _format_family_member(family_member: dict[str, object] | None) -> str:
    if family_member is None:
        return "Unknown Messenger sender. Be helpful, but do not assume which family member this is."

    aliases = family_member.get("aliases") or []
    aliases_text = ", ".join(str(alias) for alias in aliases) if aliases else "None"
    return (
        f"- member_key: {family_member['member_key']}\n"
        f"- full_name: {family_member['full_name']}\n"
        f"- preferred_name: {family_member['preferred_name']}\n"
        f"- relationship_label: {family_member['relationship_label']}\n"
        f"- aliases: {aliases_text}\n"
        "Use the preferred name naturally when it fits. Do not ask this person who they are."
    )


def _format_messenger_contact(messenger_contact: dict[str, object] | None) -> str:
    if messenger_contact is None:
        return "No Messenger profile lookup data available."

    first_name = str(messenger_contact.get("first_name") or "").strip()
    last_name = str(messenger_contact.get("last_name") or "").strip()
    full_name = f"{first_name} {last_name}".strip() or "Unknown"
    family_member_key = messenger_contact.get("family_member_key") or "None"
    return (
        f"- name: {full_name}\n"
        f"- first_name: {first_name or 'Unknown'}\n"
        f"- family_member_key: {family_member_key}\n"
        "If this contact is not a linked family member, you may use their first name naturally, "
        "but do not call them a family role."
    )


def _user_content(message: str, image_urls: list[str]) -> str | list[dict[str, Any]]:
    if not image_urls:
        return message

    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": message or "Please look at this photo and help the family member.",
        }
    ]
    for image_url in image_urls[:3]:
        openai_image_url = _download_image_data_url(image_url) or image_url
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": openai_image_url,
                },
            }
        )
    return content


def _download_image_data_url(image_url: str) -> str | None:
    request = Request(image_url, headers={"User-Agent": "TitoMarlonFamilyAssistant/1.0"})
    try:
        with urlopen(request, timeout=10) as response:
            content_type = response.headers.get_content_type()
            if not content_type.startswith("image/"):
                return None
            image_bytes = response.read(MAX_IMAGE_BYTES + 1)
    except (OSError, URLError, ValueError):
        return None

    if len(image_bytes) > MAX_IMAGE_BYTES:
        logger.warning("Image skipped because it is larger than %s bytes", MAX_IMAGE_BYTES)
        return None

    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{content_type};base64,{encoded}"
