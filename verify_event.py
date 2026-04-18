import json
import os
import sqlite3
import hashlib
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "events.db")


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_event(event_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT payload_json, event_hash
        FROM raw_events
        WHERE id = ?
    """, (event_id,))
    row = cur.fetchone()

    if not row:
        print(f"[FAIL] Event id {event_id} not found")
        conn.close()
        return

    payload_json, stored_event_hash = row
    payload = json.loads(payload_json)
    recomputed_event_hash = sha256_hex(canonical_json(payload))

    print(f"Event ID:            {event_id}")
    print(f"Stored Event Hash:   {stored_event_hash}")
    print(f"Recomputed Hash:     {recomputed_event_hash}")
    print(f"Event Verified:      {stored_event_hash == recomputed_event_hash}")

    cur.execute("""
        SELECT id, raw_event_id, event_hash, prev_hash, block_hash, created_at
        FROM ledger
        WHERE raw_event_id = ?
    """, (event_id,))
    ledger_row = cur.fetchone()

    if ledger_row:
        ledger_id, raw_event_id, event_hash, prev_hash, block_hash, created_at = ledger_row
        block_material = canonical_json({
            "raw_event_id": raw_event_id,
            "created_at": created_at,
            "event_hash": event_hash,
            "prev_hash": prev_hash
        })
        recomputed_block_hash = sha256_hex(block_material)

        print(f"Ledger ID:           {ledger_id}")
        print(f"Stored Block Hash:   {block_hash}")
        print(f"Recomputed Block:    {recomputed_block_hash}")
        print(f"Ledger Verified:     {block_hash == recomputed_block_hash}")
    else:
        print("[WARN] No ledger entry found for this event")

    conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_event.py <event_id>")
        sys.exit(1)

    verify_event(int(sys.argv[1]))
