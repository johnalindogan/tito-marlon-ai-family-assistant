import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import MessageRequest
from app.service import process_message


def main() -> None:
    response = process_message(
        MessageRequest(
            sender_id="openai-smoke-test",
            message="Kumusta Tito Marlon? Sagot ka ng maikli sa Taglish.",
        )
    )
    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
