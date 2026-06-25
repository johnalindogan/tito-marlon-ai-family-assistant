from app import database
from app.ai import extract_memories, generate_reply
from app.outbound_images import outbound_image_urls_for_message
from app.schemas import FamilyMemberProfile, MessageRequest, MessageResponse, MessengerContactProfile


def process_message(payload: MessageRequest) -> MessageResponse:
    memories_saved = extract_memories(payload.message) if payload.message else []
    outbound_image_urls = outbound_image_urls_for_message(payload.message)
    stored_user_message = payload.message
    if payload.image_urls:
        stored_user_message = f"{payload.message}\n[Photo attached]".strip()

    with database.session_scope() as session:
        family_member = None
        messenger_contact = None
        memory_identity_id = payload.sender_id
        if session is not None:
            if payload.messenger_profile is not None:
                messenger_contact = database.upsert_messenger_contact(
                    session,
                    payload.sender_id,
                    payload.messenger_profile.model_dump(),
                )
            else:
                messenger_contact = database.load_messenger_contact(session, payload.sender_id)

            family_member_key = (
                str(messenger_contact["family_member_key"])
                if messenger_contact and messenger_contact.get("family_member_key")
                else None
            )
            if family_member_key:
                family_member = database.load_family_member_by_key(session, family_member_key)
            if family_member is None:
                family_member = database.load_family_member_by_sender_id(session, payload.sender_id)
            if family_member is not None:
                memory_identity_id = str(family_member["member_key"])

            database.save_chat_message(session, payload.sender_id, "user", stored_user_message)
            for memory in memories_saved:
                database.upsert_memory(
                    session,
                    memory_identity_id,
                    memory.memory_key,
                    memory.memory_value,
                )
            recent_chat = database.load_recent_chat(session, payload.sender_id)
            memory = database.load_memory(session, memory_identity_id)
        else:
            recent_chat = []
            memory = {}
            family_member = None
            messenger_contact = None

        reply = generate_reply(
            payload.sender_id,
            payload.message,
            payload.image_urls,
            family_member,
            messenger_contact,
            recent_chat,
            memory,
        )

        if session is not None:
            database.save_chat_message(session, payload.sender_id, "assistant", reply)

    return MessageResponse(
        reply=reply,
        memories_saved=memories_saved,
        outbound_image_urls=outbound_image_urls,
        identified_family_member=(
            FamilyMemberProfile.model_validate(family_member) if family_member is not None else None
        ),
        messenger_contact=(
            MessengerContactProfile.model_validate(messenger_contact)
            if messenger_contact is not None
            else None
        ),
    )
