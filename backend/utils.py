# backend/utils.py
from bson import ObjectId
from datetime import datetime

def doc_to_json(doc):
    if not doc:
        return None
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out

# Guardrails blocklist
BLOCKED_KEYWORDS = [
    "hack",
    "bomb",
    "kill",
    "terrorist",
    "suicide",
    "murder",
    "drugs",
    "weapon",
    "rape",
    "abuse",
    "nude"
]

def check_guardrails(message: str) -> bool:
    """
    Returns False if the message contains harmful or inappropriate keywords.
    """
    for word in BLOCKED_KEYWORDS:
        if word in message.lower():
            return False
    return True

# backend/utils.py

def is_safe_message(message: str) -> bool:
    """
    Very simple guardrail: block unsafe keywords.
    You can expand this list as needed.
    """
    unsafe_keywords = ["sex", "drugs", "violence", "bomb", "attack", "kill"]
    msg_lower = message.lower()
    for word in unsafe_keywords:
        if word in msg_lower:
            return False
    return True
