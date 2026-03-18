# ⌚ The Wrist Pad Wiring Guide

The wrist pad serves as the "Remote Control" for the Blind Assist Hat. Because visually impaired users need a reliable and tactile way to control the AI, we use four physical push-buttons mounted on a wrist strap.

## How do the buttons work?
When a user presses a button down, it connects two pieces of metal inside the button switch. This closes an electrical loop, allowing a tiny bit of electricity to flow into the Raspberry Pi's "GPIO Pin". The Pi instantly senses this flow and triggers the Voice AI or Camera to act.

## Physical Wiring
Each button has two metal legs underneath it.

1. **Leg 1:** Connects to the specific GPIO Pin (see below).
2. **Leg 2:** Connects to the **Ground (GND)** on the Raspberry Pi.

*(For efficiency, you can daisy-chain all four Button Leg 2s together and run just one single Ground wire back to the Raspberry Pi).*

## The Map

| Location on Wrist | Button | Connect Leg 1 to... | Function for the User |
|-------------------|--------|---------------------|-----------------------|
| Top Left          | **B1** | `GPIO Pin 16`       | Describe surroundings |
| Top Right         | **B2** | `GPIO Pin 20`       | Read text out loud    |
| Bottom Left       | **B3** | `GPIO Pin 21`       | Start Navigation      |
| Bottom Right      | **B4** | `GPIO Pin 12`       | Repeat last output    |

## Tips for the Assembly Team
- Ensure the buttons have a satisfying "click" so the user can feel that they pressed it successfully.
- The wires connecting the wrist pad to the hat should run down the user’s sleeve, so make sure they are flexible and reinforced so they don't break during arm movements.
