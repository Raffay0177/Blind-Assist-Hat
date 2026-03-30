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

def analyze_image(prompt_text, filename="capture.jpg"):
    """ Captures a frame and evaluates it against GPT-4 Vision """
    if not client:
        return f"Placeholder response for: {prompt_text}. OpenAI API key not configured yet."
        
    img_path = capture_image(filename)
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
    prompt = (
        "You are a visual navigation assistant for a completely blind user wearing a chest-mounted camera. "
        "Describe exactly what is straight ahead from their point of view. "
        "Focus entirely on immediate physical obstacles, trip hazards, overhead dangers, and the general layout of the walking path. "
        "Be extremely concise and precise. Explicitly flag any dangerous objects, sudden drops, or approaching people. "
        "Do not describe background scenery or colors unless it is directly relevant to safety."
    )
    return analyze_image(prompt)

def read_text():
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captures/text_{timestamp}.jpg"
    print(f"DEBUG: Saving OCR capture to {filename}")
    return analyze_image("I am a vision assistant for the blind. Please identify any text, signs, labels, or handwriting in this image. Read the text exactly as it appears. If multiple blocks of text exist, read them all clearly. If no text is visible, say 'No text detected'.", filename=filename)
