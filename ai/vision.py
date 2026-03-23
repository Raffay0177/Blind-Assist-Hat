import os
import base64
from openai import OpenAI
from config.settings import OPENAI_API_KEY
from sensors.camera import capture_image

# Only initialize the client if a key is provided
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def encode_image(image_path):
    """ Encodes an image to Base64 to be sent in the OpenAI Payload """
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(prompt_text):
    """ Captures a frame and evaluates it against GPT-4 Vision """
    if not client:
        return f"Placeholder response for: {prompt_text}. OpenAI API key not configured yet."
        
    img_path = capture_image()
    if not img_path:
        return "Failed to capture image from camera."
        
    if img_path == "mocked_capture.jpg":
        return f"Mocked vision analysis response for: {prompt_text}."
        
    base64_image = encode_image(img_path)
    
    try:
        response = client.chat.completions.create(
          model="gpt-4o",
          messages=[
            {
              "role": "user",
              "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
              ]
            }
          ],
          max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API Error: {str(e)}"

def describe_scene():
    return analyze_image("Describe exactly what is straight ahead in this scene. Be brief, focusing only on immediate obstacles, objects, and people.")

def read_text():
    return analyze_image("Identify and read aloud any prominent text, signs, or labels in this image. Only output the exact text found, or say 'No text detected' if none is found.")
