# 🔌 General Wiring Guide (Sensors & Buttons)

This guide explains how the different physical parts of the hat connect to the "Brain" (the Raspberry Pi). Don't worry if you're new to hardware; we'll keep it simple!

## What is a GPIO Pin?
A **GPIO pin** is just a tiny metal spike on the Raspberry Pi where we can plug in a wire. 
- Some pins send electricity (Power).
- Some connect to ground (GND - necessary to complete the electrical loop).
- Others send or receive data from our sensors.

## 🦇 Ultrasonic Sensors (Distance Sensors)
We have three of these to detect objects. They work like bat echolocation! Each sensor has a **Trigger** (sends out a sound wave) and an **Echo** (listens for the sound to bounce back from an object).

| Sensor Location | Trigger Pin | Echo Pin | What it does |
|-----------------|-------------|----------|--------------|
| **Front Sensor**| Pin 23      | Pin 24   | Detects objects straight ahead |
| **Left Sensor** | Pin 17      | Pin 27   | Detects objects entering from the left |
| **Right Sensor**| Pin 5       | Pin 6    | Detects objects entering from the right |

*(Note: These 5V sensors need a "Voltage Divider" to safely connect their Echo pins to our 3.3V Raspberry Pi. See `voltage_divider.md` for a simple explanation!)*

## 🎛️ Wrist Button Pad
The wrist pad has four buttons. When clicked, they send a tiny signal to a specific pin so the computer knows what the user wants to do.

| Button | Pin connected | What it tells the system to do |
|--------|---------------|--------------------------------|
| **Button 1** | Pin 16  | "Describe the scene!" |
| **Button 2** | Pin 20  | "Read text or signs!" |
| **Button 3** | Pin 21  | "Toggle Navigation mode!" |
| **Button 4** | Pin 12  | "Repeat your last message!" |

**Golden Rule:** Always ensure the device is completely powered OFF before plugging or unplugging any wires!
