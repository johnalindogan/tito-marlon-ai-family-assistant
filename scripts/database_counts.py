import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import session_scope


def main() -> None:
    with session_scope() as session:
        if session is None:
            raise RuntimeError("DATABASE_URL is not configured")
        chat_count = session.execute(text("SELECT COUNT(*) FROM chat_messages")).scalar_one()
        memory_count = session.execute(text("SELECT COUNT(*) FROM family_memory")).scalar_one()
        member_count = session.execute(text("SELECT COUNT(*) FROM family_members")).scalar_one()
        contact_count = session.execute(text("SELECT COUNT(*) FROM messenger_contacts")).scalar_one()
        print(f"chat_messages={chat_count}")
        print(f"family_memory={memory_count}")
        print(f"family_members={member_count}")
        print(f"messenger_contacts={contact_count}")


if __name__ == "__main__":
    main()
