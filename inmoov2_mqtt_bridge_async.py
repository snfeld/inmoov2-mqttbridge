#!/usr/bin/env python3
"""InMoov2 MQTT Bridge - Async version with asyncio + paho-mqtt.

Uses asyncio for non-blocking operation with paho-mqtt's loop_start().
This version is fully async and more efficient than the sync version.

Requires: pip install paho-mqtt aiohttp
Usage: python3 inmoov2_mqtt_bridge_async.py [poll_interval_seconds]
"""

import json
import asyncio
import aiohttp
import sys
import threading
import queue
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


class InMoov2BridgeAsync:
    def __init__(self, poll_interval=POLL_INTERVAL):
        self.poll_interval = poll_interval
        self.last_status = {}
        self.last_config = {}
        self.running = False
        self.session = None
        self.loop = None
        self.message_queue = asyncio.Queue()
        # Thread-safe queue for passing messages from MQTT thread to asyncio
        self._msg_queue = queue.Queue()
        self._mqtt_client = None
        self._mqtt_thread = None
        self._setup_mqtt_client()
        
    def _setup_mqtt_client(self):
        """Set up the MQTT client with callbacks."""
        self._mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="inmoov2_bridge",
            protocol=mqtt.MQTTv311
        )
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message

    def time(self):
        return datetime.now().strftime('%H:%M:%S')

    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print(f"[{self.time()}] Connected to MQTT broker")
            self._subscribe_all()
            print(f"[{self.time()}] Subscribed to: inmoov2/servos/# and inmoov2/cmd/#")
        else:
            print(f"[{self.time()}] MQTT connect failed: {rc}")

    def _subscribe_all(self):
        for topic in [
            f"{MQTT_BASE}/servos/#",
            f"{MQTT_BASE}/cmd/#",
        ]:
            self._mqtt_client.subscribe(topic, qos=1)
            print(f"[{self.time()}] Subscribed: {topic}")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        print(f"[on_message] {topic}", flush=True)
        try:
            self._msg_queue.put((topic, payload), block=False)
        except queue.Full:
            print(f"[on_message] queue full, dropping message", flush=True)

    async def message_dispatcher(self):
        while self.running:
            try:
                # Get message from thread-safe queue
                topic, payload = self._msg_queue.get(timeout=0.1)
                print(f"[{self.time()}] MSG: topic={topic}")
                try:
                    parts = topic.split("/")
                    if len(parts) < 3:
                        continue
                    if len(parts) >= 3 and parts[1] == "servos" and parts[-1] == "cmd":
                        entity = "/".join(parts[2:-1])
                        print(f"[{self.time()}] CMD: entity={entity}")
                        await self.handle_cmd(entity, payload)
                    elif len(parts) >= 3 and parts[1] == "cmd" and parts[2] == "config":
                        entity = "/".join(parts[3:]) if len(parts) > 3 else "all"
                        print(f"[{self.time()}] Config: entity={entity}")
                        await self.handle_config(entity, payload)
                    elif len(parts) >= 3 and parts[1] == "cmd" and parts[2] == "config" and len(parts) > 3 and parts[3] == "poll":
                        print(f"[{self.time()}] Poll")
                        await self.handle_poll(payload)
                    elif len(parts) >= 3 and parts[1] == "cmd":
                        print(f"[{self.time()}] CMD (simple): entity={parts[2]}")
                        # Handle simple cmd format: inmoov2/cmd/{servo}
                        if "." in parts[2]:
                            await self.handle_cmd(parts[2], payload)
                    else:
                        print(f"[{self.time()}] Ignoring: {topic}")
                except Exception as e:
                    print(f"[{self.time()}] Error handling {topic}: {e}")
                self._msg_queue.task_done()
            except queue.Empty:
                continue
            except asyncio.CancelledError:
                break

    async def handle_cmd(self, entity, payload):
        try:
            data = json.loads(payload)
            pos = data.get("pos")
            if pos is None:
                return
            if entity in ALL_GROUPS:
                await self.move_group(entity, pos)
            elif "." in entity:
                await self.move_servo(entity, pos)
        except Exception as e:
            print(f"[{self.time()}] Error handling cmd: {e}")

    async def handle_config(self, entity, payload):
        try:
            data = json.loads(payload)
            if entity in ALL_GROUPS:
                for key, value in data.items():
                    if key in ["speed", "idleTimeout"]:
                        for param in ALL_GROUPS[entity]["params"]:
                            servo = f"{ALL_GROUPS[entity]['prefix']}.{param}"
                            try:
                                resp = await self.session.post(
                                    f"{REST_API}/{servo}/set{key.capitalize()}",
                                    data=json.dumps([value]), timeout=5
                                )
                                print(f"[{self.time()}] Set {key}={value} on {servo}")
                            except Exception as e:
                                print(f"[{self.time()}] Error setting {key} on {servo}: {e}")
            elif "." in entity:
                for key, value in data.items():
                    if key in ["speed", "idleTimeout"]:
                        try:
                            resp = await self.session.post(
                                f"{REST_API}/{entity}/set{key.capitalize()}",
                                data=json.dumps([value]), timeout=5
                            )
                            print(f"[{self.time()}] Set {key}={value} on {entity}")
                        except Exception as e:
                            print(f"[{self.time()}] Error setting {key} on {entity}: {e}")
        except Exception as e:
            print(f"[{self.time()}] Error handling config: {e}")

    async def handle_poll(self, payload):
        try:
            data = json.loads(payload)
            new_interval = data.get("interval", self.poll_interval)
            if new_interval >= 0:
                self.poll_interval = new_interval
                print(f"[{self.time()}] Poll interval changed to {new_interval}s")
        except Exception as e:
            print(f"[{self.time()}] Error changing poll interval: {e}")

    async def move_servo(self, servo, pos):
        try:
            url = f"{REST_API}/{servo}/moveTo"
            payload = json.dumps([pos]) if not isinstance(pos, list) else json.dumps(pos)
            async with self.session.post(url, data=payload, headers={"Content-Type": "application/json"}, timeout=5) as resp:
                print(f"[{self.time()}] Moved {servo} to {pos}")
        except Exception as e:
            print(f"[{self.time()}] Error moving {servo}: {e}")

    async def move_group(self, group_name, pos):
        try:
            group = ALL_GROUPS[group_name]
            url = f"{REST_API}{group['url']}"
            if isinstance(pos, (int, float)):
                pos = [pos] * len(group["params"])
            params_str = "/".join(str(p) for p in pos)
            url = f"{url}/{params_str}"
            async with self.session.get(url, timeout=10) as resp:
                print(f"[{self.time()}] Moved {group_name} to {pos}")
        except Exception as e:
            print(f"[{self.time()}] Error moving {group_name}: {e}")

    async def poll_loop(self):
        try:
            while self.running:
                if self.poll_interval > 0:
                    await self.poll_all()
                await asyncio.sleep(self.poll_interval)
        except asyncio.CancelledError:
            pass

    async def poll_all(self):
        try:
            for group_name, group_data in ALL_GROUPS.items():
                for i, param in enumerate(group_data["params"]):
                    servo = f"{group_data['prefix']}.{param}"
                    try:
                        async with self.session.get(f"{REST_API}/{servo}", timeout=5) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                status = {
                                    "pos": data.get("currentInputPos"),
                                    "target": data.get("targetPos"),
                                    "moving": data.get("isMoving")
                                }
                                topic_status = f"{MQTT_BASE}/servos/{servo}/status"
                                if json.dumps(status) != json.dumps(self.last_status.get(topic_status)):
                                    self.last_status[topic_status] = status
                                    await self.publish(topic_status, json.dumps(status), retain=True)
                    except Exception:
                        pass
                await asyncio.sleep(0.05)
        except Exception as e:
            print(f"[{self.time()}] Poll error: {e}")

    async def publish(self, topic, payload, retain=False):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            self._mqtt_client.publish,
            topic,
            payload,
            False,  # qos
            retain
        )

    async def start(self):
        self.running = True
        self.session = aiohttp.ClientSession()
        self.loop = asyncio.get_running_loop()
        
        # Connect and start MQTT loop in a background thread
        self._mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
        
        # Start the MQTT network loop in a background thread
        mqtt_thread = threading.Thread(
            target=self._mqtt_client.loop_start,
            daemon=True
        )
        mqtt_thread.start()
        
        print(f"[{self.time()}] MQTT thread created")
        print(f"[{self.time()}] Async bridge started (poll_interval={self.poll_interval}s)")

        # Run poll_loop and message_dispatcher concurrently
        poll_task = asyncio.create_task(self.poll_loop())
        dispatch_task = asyncio.create_task(self.message_dispatcher())
        
        # Wait for both tasks to complete
        await asyncio.gather(poll_task, dispatch_task)

    async def stop(self):
        self.running = False
        if self._mqtt_client:
            self._mqtt_client.loop_stop()
        if self.session:
            await self.session.close()


async def main():
    poll_interval = int(sys.argv[1]) if len(sys.argv) > 1 else POLL_INTERVAL
    bridge = InMoov2BridgeAsync(poll_interval)
    try:
        await bridge.start()
    except KeyboardInterrupt:
        print(f"\n[{bridge.time()}] Bridge stopped")
    finally:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())