# InMoov2 MQTT Bridge - Architektur & Topic-Struktur

## ÜBERSICHT

Die MQTT Bridge übersetzt MQTT Messages in HTTP REST API Calls zu InMoov2/MRL.

- **Broker:** MQTT Broker (Mosquitto, EMQTT, etc.)
- **Bridge:** Python-Service auf demselben Server wie MRL
- **Ziel:** Vollständige Steuerung aller 27 Servos + Gruppenbewegungen

---

## TOPIC-STRUKTUR

```
inmoov2/servos/{servo}/cmd        # Einzelnes Servo bewegen
inmoov2/servos/{servo}/status     # Einzelnes Servo Status
inmoov2/servos/{servo}/config     # Einzelnes Servo Konfiguration

inmoov2/servos/{gruppe}/cmd       # Gruppe bewegen (High-Level)
inmoov2/servos/{gruppe}/status    # Gruppe Status
inmoov2/servos/{gruppe}/config    # Gruppe Konfiguration

inmoov2/cmd/[init|stop|reset]     # Globale Steuerung
inmoov2/status/system             # System-Status
```

---

## EINDÜTIGE TOPIC-REFERENZ

### Einzelne Servos (27 Servos)

| Servo | CMD Topic | STATUS Topic | CONFIG Topic |
|-------|-----------|--------------|--------------|
| i01.rightArm.bicep | `inmoov2/servos/i01.rightArm.bicep/cmd` | `inmoov2/servos/i01.rightArm.bicep/status` | `inmoov2/servos/i01.rightArm.bicep/config` |
| i01.rightArm.rotate | `inmoov2/servos/i01.rightArm.rotate/cmd` | `inmoov2/servos/i01.rightArm.rotate/status` | `inmoov2/servos/i01.rightArm.rotate/config` |
| i01.rightArm.shoulder | `inmoov2/servos/i01.rightArm.shoulder/cmd` | `inmoov2/servos/i01.rightArm.shoulder/status` | `inmoov2/servos/i01.rightArm.shoulder/config` |
| i01.rightArm.omoplate | `inmoov2/servos/i01.rightArm.omoplate/cmd` | `inmoov2/servos/i01.rightArm.omoplate/status` | `inmoov2/servos/i01.rightArm.omoplate/config` |
| i01.leftArm.bicep | `inmoov2/servos/i01.leftArm.bicep/cmd` | `inmoov2/servos/i01.leftArm.bicep/status` | `inmoov2/servos/i01.leftArm.bicep/config` |
| i01.leftArm.rotate | `inmoov2/servos/i01.leftArm.rotate/cmd` | `inmoov2/servos/i01.leftArm.rotate/status` | `inmoov2/servos/i01.leftArm.rotate/config` |
| i01.leftArm.shoulder | `inmoov2/servos/i01.leftArm.shoulder/cmd` | `inmoov2/servos/i01.leftArm.shoulder/status` | `inmoov2/servos/i01.leftArm.shoulder/config` |
| i01.leftArm.omoplate | `inmoov2/servos/i01.leftArm.omoplate/cmd` | `inmoov2/servos/i01.leftArm.omoplate/status` | `inmoov2/servos/i01.leftArm.omoplate/config` |
| i01.rightHand.thumb | `inmoov2/servos/i01.rightHand.thumb/cmd` | `inmoov2/servos/i01.rightHand.thumb/status` | `inmoov2/servos/i01.rightHand.thumb/config` |
| i01.rightHand.index | `inmoov2/servos/i01.rightHand.index/cmd` | `inmoov2/servos/i01.rightHand.index/status` | `inmoov2/servos/i01.rightHand.index/config` |
| i01.rightHand.majeure | `inmoov2/servos/i01.rightHand.majeure/cmd` | `inmoov2/servos/i01.rightHand.majeure/status` | `inmoov2/servos/i01.rightHand.majeure/config` |
| i01.rightHand.ringFinger | `inmoov2/servos/i01.rightHand.ringFinger/cmd` | `inmoov2/servos/i01.rightHand.ringFinger/status` | `inmoov2/servos/i01.rightHand.ringFinger/config` |
| i01.rightHand.pinky | `inmoov2/servos/i01.rightHand.pinky/cmd` | `inmoov2/servos/i01.rightHand.pinky/status` | `inmoov2/servos/i01.rightHand.pinky/config` |
| i01.rightHand.wrist | `inmoov2/servos/i01.rightHand.wrist/cmd` | `inmoov2/servos/i01.rightHand.wrist/status` | `inmoov2/servos/i01.rightHand.wrist/config` |
| i01.leftHand.thumb | `inmoov2/servos/i01.leftHand.thumb/cmd` | `inmoov2/servos/i01.leftHand.thumb/status` | `inmoov2/servos/i01.leftHand.thumb/config` |
| i01.leftHand.index | `inmoov2/servos/i01.leftHand.index/cmd` | `inmoov2/servos/i01.leftHand.index/status` | `inmoov2/servos/i01.leftHand.index/config` |
| i01.leftHand.majeure | `inmoov2/servos/i01.leftHand.majeure/cmd` | `inmoov2/servos/i01.leftHand.majeure/status` | `inmoov2/servos/i01.leftHand.majeure/config` |
| i01.leftHand.ringFinger | `inmoov2/servos/i01.leftHand.ringFinger/cmd` | `inmoov2/servos/i01.leftHand.ringFinger/status` | `inmoov2/servos/i01.leftHand.ringFinger/config` |
| i01.leftHand.pinky | `inmoov2/servos/i01.leftHand.pinky/cmd` | `inmoov2/servos/i01.leftHand.pinky/status` | `inmoov2/servos/i01.leftHand.pinky/config` |
| i01.leftHand.wrist | `inmoov2/servos/i01.leftHand.wrist/cmd` | `inmoov2/servos/i01.leftHand.wrist/status` | `inmoov2/servos/i01.leftHand.wrist/config` |
| i01.head.neck | `inmoov2/servos/i01.head.neck/cmd` | `inmoov2/servos/i01.head.neck/status` | `inmoov2/servos/i01.head.neck/config` |
| i01.head.rothead | `inmoov2/servos/i01.head.rothead/cmd` | `inmoov2/servos/i01.head.rothead/status` | `inmoov2/servos/i01.head.rothead/config` |
| i01.head.rollNeck | `inmoov2/servos/i01.head.rollNeck/cmd` | `inmoov2/servos/i01.head.rollNeck/status` | `inmoov2/servos/i01.head.rollNeck/config` |
| i01.head.eyeX | `inmoov2/servos/i01.head.eyeX/cmd` | `inmoov2/servos/i01.head.eyeX/status` | `inmoov2/servos/i01.head.eyeX/config` |
| i01.head.eyeY | `inmoov2/servos/i01.head.eyeY/cmd` | `inmoov2/servos/i01.head.eyeY/status` | `inmoov2/servos/i01.head.eyeY/config` |
| i01.head.jaw | `inmoov2/servos/i01.head.jaw/cmd` | `inmoov2/servos/i01.head.jaw/status` | `inmoov2/servos/i01.head.jaw/config` |
| i01.head.eyelidLeft | `inmoov2/servos/i01.head.eyelidLeft/cmd` | `inmoov2/servos/i01.head.eyelidLeft/status` | `inmoov2/servos/i01.head.eyelidLeft/config` |
| i01.head.eyelidRight | `inmoov2/servos/i01.head.eyelidRight/cmd` | `inmoov2/servos/i01.head.eyelidRight/status` | `inmoov2/servos/i01.head.eyelidRight/config` |
| i01.torso.topStom | `inmoov2/servos/i01.torso.topStom/cmd` | `inmoov2/servos/i01.torso.topStom/status` | `inmoov2/servos/i01.torso.topStom/config` |
| i01.torso.midStom | `inmoov2/servos/i01.torso.midStom/cmd` | `inmoov2/servos/i01.torso.midStom/status` | `inmoov2/servos/i01.torso.midStom/config` |
| i01.torso.lowStom | `inmoov2/servos/i01.torso.lowStom/cmd` | `inmoov2/servos/i01.torso.lowStom/status` | `inmoov2/servos/i01.torso.lowStom/config` |

### Gruppen (High-Level)

| Gruppe | CMD Topic | STATUS Topic | CONFIG Topic |
|--------|-----------|--------------|--------------|
| Rechter Arm | `inmoov2/servos/rightArm/cmd` | `inmoov2/servos/rightArm/status` | `inmoov2/servos/rightArm/config` |
| Linker Arm | `inmoov2/servos/leftArm/cmd` | `inmoov2/servos/leftArm/status` | `inmoov2/servos/leftArm/config` |
| Rechte Hand | `inmoov2/servos/rightHand/cmd` | `inmoov2/servos/rightHand/status` | `inmoov2/servos/rightHand/config` |
| Linke Hand | `inmoov2/servos/leftHand/cmd` | `inmoov2/servos/leftHand/status` | `inmoov2/servos/leftHand/config` |
| Kopf | `inmoov2/servos/head/cmd` | `inmoov2/servos/head/status` | `inmoov2/servos/head/config` |
| Torso | `inmoov2/servos/torso/cmd` | `inmoov2/servos/torso/status` | `inmoov2/servos/torso/config` |

### Globale Steuerung

| Funktion | Topic |
|----------|-------|
| System-Status | `inmoov2/status/system` |
| Initialisierung | `inmoov2/cmd/init` |
| Neustart | `inmoov2/cmd/reset` |

---

## MESSAGE-FORMATE

### CMD (Bewegung)

#### Einzelnes Servo
```json
{"pos": 90}           // Grad
```

#### Gruppe
```json
{"pos": [0, 90, 0, 90]}  // Array in definierter Reihenfolge
```

#### Config-Werte setzen
```json
{"speed": 60}                    // Geschwindigkeit
{"rest": 45}                     // Ruhewert
{"idleTimeout": 5000}            // Auto-Disable nach 5s
```

### STATUS (aktuelle Werte)

```json
{
  "pos": 30,
  "target": 30,
  "moving": false
}
```

#### Gruppen-Status
```json
{
  "bicep": {"pos": 30, "target": 30},
  "rotate": {"pos": 90, "target": 90},
  "shoulder": {"pos": 0, "target": 0},
  "omoplate": {"pos": 80, "target": 80}
}
```

### CONFIG (Konfiguration lesen/schreiben)

```json
{
  "speed": 45,
  "rest": 0,
  "idleTimeout": 3000,
  "autoDisable": true,
  "enabled": true,
  "inverted": false,
  "clip": true,
  "pin": "8"
}
```

---

## POLL-STRATEGIE

### Standard (Empfohlen)
- **Intervall:** 5 Sekunden
- **Retain:** Alle Messages mit `retain=true`
- **Lastige:** Nur bei Wertänderung
- **Beim Start:** Erstes Pollen nach 1s

### Konfigurierbar
```
inmoov2/cmd/config/poll {"interval": 5}  // 5 Sekunden
inmoov2/cmd/config/poll {"interval": 1}  // 1 Sekunde
inmoov2/cmd/config/poll {"interval": 0}  // Nur Event-driven (kein Pollen)
```

### Belastung (bei 30 Servos x 5s)
- **REST Calls/Sek:** ~6
- **Server-Last:** Niedrig
- **Empfohlen für Produktion**

---

## MQTT BEISPIELE

### Servo bewegen
```bash
mosquitto_pub -t "inmoov2/servos/i01.rightArm.bicep/cmd" -m '{"pos":90}'
```

### Arm bewegen (High-Level)
```bash
mosquitto_pub -t "inmoov2/servos/rightArm/cmd" -m '{"pos":[0,90,0,90]}'
```

### Status abonnieren
```bash
mosquitto_sub -t "inmoov2/servos/#/status" -v
```

### Config lesen
```bash
mosquitto_sub -t "inmoov2/servos/i01.rightArm.bicep/config"
```

### Config setzen
```bash
mosquitto_pub -t "inmoov2/servos/i01.rightArm.bicep/config" -m '{"speed":60,"idleTimeout":5000}'
```

---

## IMPLEMENTIERUNG

### Bridge-Architektur
```
MQTT Client -> Bridge -> REST API -> InMoov2/MRL
   |              |         |
   |              |         +-> i01.rightArm.bicep/moveTo
   |              +-> HTTP POST
   +-> subscribe/unsubscribe
```

### Python Bridge
```python
class InMoov2Bridge:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.rest_url = "http://localhost:8888/api/service"
        self.poll_interval = 5
        
    def on_message(self, topic, payload):
        if topic.endswith("/cmd"):
            self.move_servo(topic, payload)
        elif topic.endswith("/config"):
            self.set_config(topic, payload)
            
    def poll_status(self):
        # Pollt alle X Sekunden REST API
        # Publish mit retain=true
        pass
```

---

## ZUSAMMENFASSUNG

| Feature | Topic-Struktur | Retain | Polling |
|---------|---------------|--------|---------|
| Bewegung | `/servos/{servo}/cmd` | Nein | Nein (sofort) |
| Status | `/servos/{servo}/status` | Ja | Ja (5s) |
| Config | `/servos/{servo}/config` | Ja | Ja (5s) |
| Gruppe | `/servos/{gruppe}/cmd` | Nein | Nein (sofort) |
| System | `/status/system` | Ja | Ja (30s) |

**Gesamt: 31 Servos + 6 Gruppen + 1 System = 38 Topics x 3 = 114 Topics**