# 🔧 Step-by-Step Hardware Assembly Guide

Welcome to the wiring portion of the Blind Assist Hat! This process is simple.

---

## Step 1: Connecting the Camera & Speaker
1. **The Camera**: Insert the camera ribbon cable straight into the `CSI` port.
2. **The Speaker**: Plug directly into the Raspberry Pi's **3.5mm audio jack**.

---

## Step 2: Wiring the Wrist Buttons
Connect each button bridging between a GPIO pin and Ground.

```mermaid
flowchart LR
    subgraph Raspberry Pi
        P_16[GPIO 16]
        P_20[GPIO 20]
        P_21[GPIO 21]
        P_12[GPIO 12]
        P_GND[Any GND Pin]
    end

    subgraph Wrist Pad
        B1((Button 1))
        B2((Button 2))
        B3((Button 3))
        B4((Button 4))
    end
    
    B1 -->|Leg 1| P_16
    B1 -->|Leg 2| P_GND

    B2 -->|Leg 1| P_20
    B2 -->|Leg 2| P_GND

    B3 -->|Leg 1| P_21
    B3 -->|Leg 2| P_GND

    B4 -->|Leg 1| P_12
    B4 -->|Leg 2| P_GND
```

---

## Step 3: Wiring the Ultrasonic Sensors

Since your specific HC-SR04 sensors are compatible with **3.3 Volts**, they can wire perfectly directly to the Raspberry Pi without any external voltage dividers!

### Ultrasonic Sensor Front Connections
| Pin | Connection |
| :--- | :--- |
| VCC | 3.3V |
| Trig | GPIO 23 |
| Echo | GPIO 24 |
| GND | GND |

### Ultrasonic Sensor Left Connections
| Pin | Connection |
| :--- | :--- |
| VCC | 3.3V |
| Trig | GPIO 17 |
| Echo | GPIO 27 |
| GND | GND |

### Ultrasonic Sensor Right Connections
| Pin | Connection |
| :--- | :--- |
| VCC | 3.3V |
| Trig | GPIO 5 |
| Echo | GPIO 6 |
| GND | GND |

### Diagram Example (Front Sensor)
```mermaid
flowchart LR
    subgraph Raspberry Pi
        P_3_3V[3.3V Pin]
        P_GND[GND Pin]
        P_23[GPIO 23]
        P_24[GPIO 24]
    end

    subgraph Front Sensor
        VCC
        TRIG
        ECHO
        GND
    end

    P_3_3V --> VCC
    P_GND --> GND
    P_23 --> TRIG
    ECHO --> P_24
```
