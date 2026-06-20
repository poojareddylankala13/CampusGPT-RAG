from modules.auth import authenticate_user, register_new_user
from modules.database import (
    add_chat_entry,
    clear_chat_history,
    delete_user,
    get_chat_history,
)


def test_chat_history_operations():
    # 1. Setup temporary user
    email = "chat_test_user@campusgpt.edu"
    password = "chat_password"
    name = "Chat Test User"

    register_new_user(name, email, password)
    user = authenticate_user(email, password)
    assert user is not None
    user_id = user["id"]

    try:
        # 2. Add chat entries
        sources = [{"document": "Handbook.pdf", "page": 1, "score": 0.95, "preview": "Syllabus details"}]

        chat_id_1 = add_chat_entry(
            user_id=user_id,
            question="What is the syllabus for CS101?",
            answer="CS101 covers introduction to computing.",
            sources=sources,
        )
        assert chat_id_1 > 0

        chat_id_2 = add_chat_entry(
            user_id=user_id,
            question="What are the passing criteria?",
            answer="Minimum passing grade is 40%.",
            sources=[],
        )
        assert chat_id_2 > 0

        # 3. Retrieve and verify chat history
        history = get_chat_history(user_id)
        assert len(history) == 2

        # Verify ordering (default is ascending by timestamp)
        assert history[0]["question"] == "What is the syllabus for CS101?"
        assert history[0]["answer"] == "CS101 covers introduction to computing."
        assert history[0]["sources"] == sources

        assert history[1]["question"] == "What are the passing criteria?"
        assert history[1]["answer"] == "Minimum passing grade is 40%."
        assert history[1]["sources"] == []

        # 4. Clear chat history and verify removal
        clear_chat_history(user_id)
        cleared_history = get_chat_history(user_id)
        assert len(cleared_history) == 0

    finally:
        # 5. Clean up temporary user
        delete_user(user_id)
