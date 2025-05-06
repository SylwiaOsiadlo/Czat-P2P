# === p2p_chat/main.py ===
from chat.peer import Peer
import threading
import time

def start_peer(port, connect_to=None):
    peer = Peer("127.0.0.1", port)
    peer.start()
    time.sleep(1)
    if connect_to:
        peer.connect("127.0.0.1", connect_to)
    time.sleep(1)
    peer.broadcast(f"Hello from {port}")
    return peer

if __name__ == "__main__":
    threading.Thread(target=start_peer, args=(5000,), daemon=True).start()
    threading.Thread(target=start_peer, args=(5001, 5000), daemon=True).start()
    threading.Thread(target=start_peer, args=(5002, 5001), daemon=True).start()

    while True:
        time.sleep(5)
