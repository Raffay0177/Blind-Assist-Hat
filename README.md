# 🧢 Blind Assist Hat (BAH)

Welcome to the **Blind Assist Hat** project! This project aims to create an affordable, smart wearable device designed to help visually impaired individuals navigate their surroundings, read text, and understand the environment around them.

## 🌟 What Does It Do?

The Blind Assist Hat uses a combination of sensors, a camera, and Artificial Intelligence (AI) to act as a pair of "digital eyes" for the user. It is controlled using a simple 4-button wrist pad.

Here are the main features:
1. **Obstacle Detection:** Uses ultrasonic sensors (like bat sonar!) on the front, left, and right to gently warn the user if they are getting too close to a wall or object.
2. **Scene Description:** At the press of a button, the AI will look through the camera and describe what is in front of the user (e.g., "There is a park bench and a tree ahead, and a clear path to the right.").
3. **Text Reading:** Can read street signs, documents, or labels out loud.
4. **Navigation Mode:** Gives turn-by-turn directional assistance.

## 🛠️ How It Works (In Plain English)

To make sense of the technical parts, here is a simple breakdown of the main components:

1. **The 'Brain' (Raspberry Pi):** A small, credit-card sized computer that processes all the data.
2. **The 'Eyes' (Camera & Sensors):** A camera takes pictures for the AI, while the ultrasonic sensors measure distance to physical objects.
3. **The 'Voice' (Speakers/Headphones):** The system talks to the user using synthesized speech (Text-to-Speech).
4. **The 'Remote' (Wrist Pad):** A small 4-button controller worn on the wrist lets the user easily tell the hat what to do without needing to see a screen.

### The Wrist Buttons
- **Button 1:** Describe the scene in front of me.
- **Button 2:** Read any text or signs you currently see.
- **Button 3:** Turn on/off Navigation mode.
- **Button 4:** Repeat the last thing you said.

---

## 🚀 Getting Started for the Technical Team

If you are a builder or technician setting this up, please follow the steps below. Other team members can skip this part!

1. Copy the `.env.example` file to a new file named `.env`.
2. Open `.env` and paste in your AI API keys (like your OpenAI or Gemini key).
3. To install all the required software on the Raspberry Pi "Brain", run the installation script in the terminal:
   ```bash
   ./install.sh
   ```
4. Check the `hardware/schematics/` folder for easy-to-read, visual wiring guides.
