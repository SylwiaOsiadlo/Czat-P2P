import json

def encode_message(sender: str, content: str) -> str:
    return json.dumps({
        'sender': sender,
        'content': content
    })

def decode_message(raw: str) -> dict:
    return json.loads(raw)