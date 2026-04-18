import json
import os
import sqlite3
import hashlib
import threading
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

DB_PATH = os.path.join(os.path.dirname(__file__), "events.db")

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = [
    ("events/lora", 0),
    ("events/lte", 0)
]

RPC_URL = "http://127.0.0.1:8545"
CHAIN_ID = 424242
ACCOUNT = "0xE3f908D24e07a569Abf2deF2d85a1D6d4C2448Be"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

nonce_lock = threading.Lock()
db_lock = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn


def init_db():
    with db_lock:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                mqtt_topic TEXT NOT NULL,
                received_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                event_hash TEXT NOT NULL UNIQUE,
                blockchain_tx_hash TEXT,
                blockchain_block_number INTEGER
            )
        """)

        conn.commit()
        conn.close()


def anchor_hash_on_chain(event_hash: str):
    with nonce_lock:
        nonce = w3.eth.get_transaction_count(ACCOUNT, "pending")

        tx = {
            "from": ACCOUNT,
            "to": ACCOUNT,
            "value": 0,
            "gas": 100000,
            "gasPrice": w3.to_wei("2", "gwei"),
            "nonce": nonce,
            "chainId": CHAIN_ID,
            "data": "0x" + event_hash
        }

        tx_hash = w3.eth.send_transaction(tx)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    return tx_hash.hex(), receipt.blockNumber


def store_event(topic: str, payload: dict):
    received_at = utc_now()
    payload_str = canonical_json(payload)
    event_hash = sha256_hex(payload_str)

    tx_hash = None
    block_number = None

    try:
        tx_hash, block_number = anchor_hash_on_chain(event_hash)
        print(
            f"[CHAIN] Anchored hash {event_hash[:12]}... "
            f"tx={tx_hash[:12]}... block={block_number}"
        )
    except Exception as e:
        import traceback
        print(f"[CHAIN-ERROR] Failed to anchor hash: {e}")
        traceback.print_exc()

    with db_lock:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO raw_events (
                source,
                mqtt_topic,
                received_at,
                payload_json,
                event_hash,
                blockchain_tx_hash,
                blockchain_block_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.get("source", "unknown"),
            topic,
            received_at,
            payload_str,
            event_hash,
            tx_hash,
            block_number
        ))

        conn.commit()
        conn.close()

    print(
        f"[OK] topic={topic} "
        f"source={payload.get('source')} "
        f"event_hash={event_hash[:12]}... "
        f"tx_hash={str(tx_hash)[:12]}..."
    )


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Connected reason_code={reason_code}")
    for topic, qos in MQTT_TOPICS:
        client.subscribe(topic, qos=qos)
        print(f"[MQTT] Subscribed to {topic}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Payload is not JSON object")
        store_event(msg.topic, payload)
    except Exception as e:
        print(f"[ERROR] Failed processing {msg.topic}: {e}")


def main():
    if not w3.is_connected():
        raise RuntimeError("Cannot connect to local Geth RPC")

    print(f"[WEB3] Connected chain_id={w3.eth.chain_id}")
    init_db()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    print("[START] Bridge service starting...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
