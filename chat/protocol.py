# === p2p_chat/chat/protocol.py ===
# Proste kodowanie i dekodowanie wiadomości w formacie JSON.

import json
from datetime import datetime

def encode_message(sender: str, content: str, msg_type: str = "message") -> str:
    return json.dumps({
        "type": msg_type,
        "sender": sender,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    })

def decode_message(raw_data: str) -> dict:
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        return {"type": "error", "content": "Invalid JSON"}