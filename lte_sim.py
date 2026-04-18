import time
import json
import random
from datetime import datetime, timezone
import paho.mqtt.publish as publish

BROKER = "localhost"
TOPIC = "events/lte"

def utc_now():
    return datetime.now(timezone.utc).isoformat()

while True:
    data = {
        "source": "lte",
        "timestamp": utc_now(),
        "ue_id": f"UE_{random.randint(1,3)}",
        "gps": f"{round(random.uniform(40.60,40.70),5)},{round(random.uniform(22.90,23.00),5)}",
        "signal": random.randint(-105, -75),
        "status": random.choice(["connected", "distress", "idle"])
    }

    publish.single(TOPIC, json.dumps(data), hostname=BROKER)
    print("Sent:", data)
    time.sleep(7)
