# ⚡ The Voltage Divider (Translating Voltages Safely)

## Why do we need this? (The Simple Explanation)

In the Blind Assist Hat, our distance sensors (the Ultrasonic HC-SR04 sensors) run on **5 Volts** of electricity.
However, the "Brain" (our Raspberry Pi computer) is very sensitive and can only handle **3.3 Volts**.

If the 5-volt sensor shouts its signal directly into the 3.3-volt brain, it will cause permanent electrical damage to the Raspberry Pi!

**Think of it like this:** The sensor is a megaphone, and the Raspberry Pi has very sensitive ears. We need to put a muffler between them so the Pi can hear the signal safely without getting hurt.

## How it works
To safely connect them, we use a simple **Voltage Divider**. This is just two tiny electrical resistors placed in the wire path. They "divide" the electrical pressure, scaling the 5V signal safely down to ~3.3V.

### How to build it for the "Echo" wire
*(You must do this for the 'Echo' wire of ALL THREE front/left/right sensors)*

1. Take the **Echo** wire coming directly from the Sensor.
2. Add a `1kΩ resistor` (Resistor 1).
3. After Resistor 1, the wire splits into two paths:
   - **Path A** goes straight into the correct Raspberry Pi GPIO Pin (e.g., Pin 24 for the front sensor).
   - **Path B** goes through a `2kΩ resistor` (Resistor 2) and then connects to the **Ground (GND)**.

By simply running the electricity through these resistors in a fork shape, the voltage drops to a safe level, and the Raspberry Pi reads the distance signal perfectly!
