import time
import json
import random
from datetime import datetime, timezone
import paho.mqtt.publish as publish

BROKER = "localhost"
TOPIC = "events/lora"

def utc_now():
    return datetime.now(timezone.utc).isoformat()

while True:
    data = {
        "source": "lora",
        "timestamp": utc_now(),
        "node_id": f"LORA_{random.randint(1,5)}",
        "temp": round(random.uniform(20, 45), 1),
        "battery": random.randint(40, 100),
        "rssi": random.randint(-125, -95),
        "alert": random.choice(["normal", "warning", "critical"])
    }

    publish.single(TOPIC, json.dumps(data), hostname=BROKER)
    print("Sent:", data)
    time.sleep(5)
