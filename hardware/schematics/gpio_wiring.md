# Complete Hardware Connection Guide (Raspberry Pi)

This document details the exact hardware connections required for the **Blind Assist Hat** system based on the current codebase configuration (`config/gpio_map.py`).

## ⚠️ Important Note on Ultrasonic Sensors (HC-SR04)
The **HC-SR04** ultrasonic sensors require 5V for power (VCC). However, the Raspberry Pi's GPIO pins operate at 3.3V and are **not** 5V tolerant.
- **Trig Pins**: Can be connected directly to the Pi's GPIO (the 3.3V out is enough to trigger the sensor).
- **Echo Pins**: MUST use a voltage divider (e.g., a 1kΩ and 2kΩ resistor) to step the 5V return signal down to 3.3V before connecting to the Pi's GPIO. Connecting the 5V Echo pin directly will damage your Raspberry Pi.

---

## 1. Ultrasonic Sensors (3x HC-SR04)
All sensors must share a common Ground (GND) with the Raspberry Pi.

| Sensor Position | Component Pin | Raspberry Pi Connection | Code Constant |
| :--- | :--- | :--- | :--- |
| **Front** | VCC | 5V Power Pin (e.g., Pin 2 or 4) | - |
| **Front** | GND | Any Ground Pin (e.g., Pin 6) | - |
| **Front** | Trig | **GPIO 23** (Pin 16) | `US_FRONT_TRIG` |
| **Front** | Echo | **GPIO 24** (Pin 18) *(via Voltage Divider)* | `US_FRONT_ECHO` |
| | | | |
| **Left** | VCC | 5V Power Pin | - |
| **Left** | GND | Any Ground Pin | - |
| **Left** | Trig | **GPIO 17** (Pin 11) | `US_LEFT_TRIG` |
| **Left** | Echo | **GPIO 27** (Pin 13) *(via Voltage Divider)* | `US_LEFT_ECHO` |
| | | | |
| **Right** | VCC | 5V Power Pin | - |
| **Right** | GND | Any Ground Pin | - |
| **Right** | Trig | **GPIO 5** (Pin 29) | `US_RIGHT_TRIG` |
| **Right** | Echo | **GPIO 6** (Pin 31) *(via Voltage Divider)* | `US_RIGHT_ECHO` |

---

## 2. Wrist Button Pad (4x Push Buttons)
The code utilizes the Raspberry Pi's internal pull-up resistors (`GPIO.PUD_UP`). Therefore, one side of each button connects to the designated GPIO pin, and the other side connects to a common Ground (GND). When pressed, the button bridges the connection to GND, triggering the action.

| Button Function | Component Pin 1 | Component Pin 2 | Code Constant |
| :--- | :--- | :--- | :--- |
| **B1: Describe Scene** | **GPIO 16** (Pin 36) | Ground (GND) | `BTN_1_SCENE` |
| **B2: Read Text** | **GPIO 20** (Pin 38) | Ground (GND) | `BTN_2_TEXT` |
| **B3: Toggle Nav Mode** | **GPIO 21** (Pin 40) | Ground (GND) | `BTN_3_NAV` |
| **B4: Repeat Last** | **GPIO 12** (Pin 32) | Ground (GND) | `BTN_4_REPEAT` |

---

## 3. Audio / Speaker Output
The software synthesizes and outputs audio natively (either via `eSpeak` for TTS or `pyaudio` for navigation alert tones). Hardware buzzers are not required.
- **Connection**: Plug any standard speaker or headphones into the Raspberry Pi's **3.5mm Audio Jack**. 
- Alternatively, if using an HDMI display with speakers, the audio can be routed through the **HDMI port**.

---

## 4. Camera Module
The vision features rely on a standard Raspberry Pi Camera Module.
- **Connection**: Connect the camera's ribbon cable directly into the **CSI Camera Port** located on the Raspberry Pi board. Ensure the silver contacts on the ribbon cable face the correct direction (typically away from the Ethernet/USB block).
