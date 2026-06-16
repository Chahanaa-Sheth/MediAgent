from collections import deque
from difflib import SequenceMatcher

# MAX MEMORY WINDOW
MAX_MESSAGES = 8

# GLOBAL CHAT STORAGE
conversation_sessions = {}


def similarity(a, b):
    return SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()


def create_session(chat_id):

    if chat_id not in conversation_sessions:

        conversation_sessions[chat_id] = deque(
            maxlen=MAX_MESSAGES
        )


def add_message(chat_id, role, content):

    create_session(chat_id)

    conversation_sessions[chat_id].append({
        "role": role,
        "content": content
    })


def get_recent_context(chat_id):

    create_session(chat_id)

    messages = list(
        conversation_sessions[chat_id]
    )

    formatted = []

    for msg in messages:

        formatted.append(
            f"{msg['role']}: {msg['content']}"
        )

    return "\n".join(formatted)


def is_new_topic(chat_id, current_message):

    create_session(chat_id)

    messages = list(
        conversation_sessions[chat_id]
    )

    if not messages:
        return True

    recent_user_messages = [

        msg["content"]

        for msg in messages

        if msg["role"] == "user"
    ]

    if not recent_user_messages:
        return True

    similarities = [

        similarity(current_message, old)

        for old in recent_user_messages
    ]

    max_similarity = max(similarities)

    return max_similarity < 0.35


def clear_session(chat_id):

    if chat_id in conversation_sessions:

        conversation_sessions[chat_id].clear()