#!/usr/bin/env python3
"""InMoov2 MQTT Bridge - Connects MQTT to InMoov2 REST API.

Uses paho-mqtt for MQTT communication and requests for REST API calls.
Runs in background threads for non-blocking operation.
"""

import json
import requests
import threading
import time
import sys
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Installing paho-mqtt...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paho-mqtt"])
    import paho.mqtt.client as mqtt

# Configuration
REST_API = "http://localhost:8888/api/service"
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_BASE = "inmoov2"
POLL_INTERVAL = 5

# Servo mapping
ARM_PARAMS = ["bicep", "rotate", "shoulder", "omoplate"]
HAND_PARAMS = ["thumb", "index", "majeure", "ringFinger", "pinky", "wrist"]
HEAD_PARAMS = ["neck", "rothead", "rollNeck", "eyeX", "eyeY", "jaw"]
TORSO_PARAMS = ["topStom", "midStom", "lowStom"]

ALL_GROUPS = {
    "rightArm": {"params": ARM_PARAMS, "prefix": "i01.rightArm", "url": "/i01.rightArm/moveTo"},
    "leftArm": {"params": ARM_PARAMS, "prefix": "i01.leftArm", "url": "/i01.leftArm/moveTo"},
    "rightHand": {"params": HAND_PARAMS, "prefix": "i01.rightHand", "url": "/i01.rightHand/moveTo"},
    "leftHand": {"params": HAND_PARAMS, "prefix": "i01.leftHand", "url": "/i01.leftHand/moveTo"},
    "head": {"params": HEAD_PARAMS, "prefix": "i01.head", "url": "/i01.head/moveTo"},
    "torso": {"params": TORSO_PARAMS, "prefix": "i01.torso", "url": "/i01.torso/moveTo"},
}


class InMoov2Bridge:
    def __init__(self, poll_interval=POLL_INTERVAL):
        self.poll_interval = poll_interval
        self.last_status = {}
        self.last_config = {}
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_HOST, MQTT_PORT, 60)
        self.poll_thread = threading.Thread(target=self.poll_loop, daemon=True)
        self.poll_thread.start()
        print(f"[{self.time()}] Bridge started (poll_interval={poll_interval}s)")

    def time(self):
        return datetime.now().strftime('%H:%M:%S')

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print(f"[{self.time()}] Connected to MQTT broker")
            self.subscribe_all()
            client.publish(f"{MQTT_BASE}/status/system",
                           json.dumps({"status": "running", "time": str(datetime.now())}),
                           retain=True)
        else:
            print(f"[{self.time()}] MQTT connect failed: {rc}")

    def subscribe_all(self):
        for topic in [
            f"{MQTT_BASE}/servos/#",
            f"{MQTT_BASE}/cmd/config/poll",
        ]:
            self.client.subscribe(topic, qos=1)
            print(f"[{self.time()}] Subscribed: {topic}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        threading.Thread(target=self.handle_message, args=(topic, payload), daemon=True).start()

    def handle_message(self, topic, payload):
        try:
            parts = topic.split("/")
            if len(parts) < 4:
                return
            if parts[1] == "servos":
                entity = parts[2]
                action = parts[3]
                if action == "cmd":
                    self.handle_cmd(entity, payload)
                elif action == "config":
                    self.handle_config(entity, payload)
            elif parts[1] == "cmd" and len(parts) >= 4:
                if parts[2:4] == ["config", "poll"]:
                    self.handle_poll(payload)
        except Exception as e:
            print(f"[{self.time()}] Error: {e}")

    def handle_cmd(self, entity, payload):
        try:
            data = json.loads(payload)
            pos = data.get("pos")
            if pos is None:
                return
            if entity in ALL_GROUPS:
                self.move_group(entity, pos)
            elif "." in entity:
                self.move_servo(entity, pos)
        except Exception as e:
            print(f"[{self.time()}] Error handling cmd: {e}")

    def handle_config(self, entity, payload):
        try:
            data = json.loads(payload)
            if entity in ALL_GROUPS:
                for key, value in data.items():
                    if key in ["speed", "idleTimeout"]:
                        for param in ALL_GROUPS[entity]["params"]:
                            servo = f"{ALL_GROUPS[entity]['prefix']}.{param}"
                            try:
                                resp = requests.post(
                                    f"{REST_API}/{servo}/set{key.capitalize()}",
                                    json=value, timeout=5
                                )
                                print(f"[{self.time()}] Set {key}={value} on {servo}")
                            except Exception as e:
                                print(f"[{self.time()}] Error setting {key} on {servo}: {e}")
            elif "." in entity:
                for key, value in data.items():
                    if key in ["speed", "idleTimeout"]:
                        try:
                            resp = requests.post(
                                f"{REST_API}/{entity}/set{key.capitalize()}",
                                json=value, timeout=5
                            )
                            print(f"[{self.time()}] Set {key}={value} on {entity}")
                        except Exception as e:
                            print(f"[{self.time()}] Error setting {key} on {entity}: {e}")
        except Exception as e:
            print(f"[{self.time()}] Error handling config: {e}")

    def handle_poll(self, payload):
        try:
            data = json.loads(payload)
            new_interval = data.get("interval", self.poll_interval)
            if new_interval >= 0:
                self.poll_interval = new_interval
                print(f"[{self.time()}] Poll interval changed to {new_interval}s")
        except Exception as e:
            print(f"[{self.time()}] Error changing poll interval: {e}")

    def move_servo(self, servo, pos):
        try:
            url = f"{REST_API}/{servo}/moveTo"
            payload = json.dumps([pos]) if not isinstance(pos, list) else json.dumps(pos)
            resp = requests.post(url, data=payload, headers={"Content-Type": "application/json"}, timeout=5)
            print(f"[{self.time()}] Moved {servo} to {pos}")
        except Exception as e:
            print(f"[{self.time()}] Error moving {servo}: {e}")

    def move_group(self, group_name, pos):
        try:
            group = ALL_GROUPS[group_name]
            # Build URL with parameters in path: /moveTo/30/120/45/50
            url = f"{REST_API}{group['url']}"
            if isinstance(pos, (int, float)):
                pos = [pos] * len(group["params"])
            params_str = "/".join(str(p) for p in pos)
            url = f"{url}/{params_str}"
            resp = requests.get(url, timeout=10)
            print(f"[{self.time()}] Moved {group_name} to {pos}")
        except Exception as e:
            print(f"[{self.time()}] Error moving {group_name}: {e}")

    def poll_loop(self):
        while True:
            if self.poll_interval > 0:
                self.poll_all()
            time.sleep(self.poll_interval)

    def poll_all(self):
        try:
            for group_name, group_data in ALL_GROUPS.items():
                for i, param in enumerate(group_data["params"]):
                    servo = f"{group_data['prefix']}.{param}"
                    try:
                        resp = requests.get(f"{REST_API}/{servo}", timeout=5)
                        if resp.status_code == 200:
                            data = resp.json()
                            status = {
                                "pos": data.get("currentInputPos"),
                                "target": data.get("targetPos"),
                                "moving": data.get("isMoving")
                            }
                            topic_status = f"{MQTT_BASE}/servos/{servo}/status"
                            if json.dumps(status) != json.dumps(self.last_status.get(topic_status)):
                                self.last_status[topic_status] = status
                                self.client.publish(topic_status, json.dumps(status), retain=True, qos=0)
                            config = {
                                "speed": data.get("speed"),
                                "rest": data.get("rest"),
                                "idleTimeout": data.get("idleTimeout"),
                            }
                            topic_config = f"{MQTT_BASE}/servos/{servo}/config"
                            if json.dumps(config) != json.dumps(self.last_config.get(topic_config)):
                                self.last_config[topic_config] = config
                                self.client.publish(topic_config, json.dumps(config), retain=True, qos=0)
                    except Exception:
                        pass
                time.sleep(0.05)
        except Exception as e:
            print(f"[{self.time()}] Poll error: {e}")


if __name__ == "__main__":
    poll_interval = int(sys.argv[1]) if len(sys.argv) > 1 else POLL_INTERVAL
    bridge = InMoov2Bridge(poll_interval)
    try:
        bridge.client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n[{bridge.time()}] Bridge stopped")