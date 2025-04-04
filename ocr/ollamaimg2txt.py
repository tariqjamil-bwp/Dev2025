import base64
from pathlib import Path
import ollama
import os
os.chdir('/home/tjamil/Dev/ocr')

# Get image path from user
path = 'ocr_test.jpeg'

# Encode image as base64
img = base64.b64encode(Path(path).read_bytes()).decode()

# Send image to model
response = ollama.chat(
  model='granite3.2-vision',  # Change this if using a different model
  messages=[
    {
      'role': 'user',
      'content': 'Extract and return only the exact text from this image without any additional commentary or description.'
        "Do not add phrases like 'The text on the sign reads as follows. or text in images is:' Return only the raw extracted text.",
      'images': [img],  # Use base64-encoded image
    }
  ],
)

# Print result
print(response['message']['content'])  # Ensure correct key for output
