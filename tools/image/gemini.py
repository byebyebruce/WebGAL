from google import genai
from google.genai import types
import base64
import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

class GeminiClient:
    def __init__(self,api_key=""):
      if api_key == "":
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
      else:
        api_key = api_key
      self.client = genai.Client(api_key=api_key)
        
    def generate_image(self, prompt, image_bytes=None):
        contents=prompt
        if image_bytes is not None:
          image = Image.open(BytesIO(image_bytes))
          contents = [(prompt), image],
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        return self.process_response(response)
    
    def process_response(self, response):
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                # Convert base64 data to bytes
                image_bytes = base64.b64decode(part.inline_data.data)
                return image_bytes

        return None        
                

# Example usage
if __name__ == "__main__":
    generator = GeminiClient()
    import sys
    prompt = ('Hi, can you create a 3d rendered image of a pig '
              'with wings and a top hat flying over a happy '
              'futuristic scifi city with lots of greenery?')
    image_data = None
    output_path = "output.png"

    if len(sys.argv) > 1:
      prompt = sys.argv[1]
    if len(sys.argv) > 2:
      image_path = sys.argv[2]
      with open(image_path, 'rb') as f:
        image_data = f.read()
    if len(sys.argv) > 3:
      output_path = sys.argv[3]

    image_bytes = generator.generate_image(prompt,image_data)

    with open(output_path, "wb") as f:
      f.write(image_bytes)
    # Attempt to open image from bytes
    #image = Image.open(BytesIO(image_bytes))
    
    # Save and display the image
    #image.save(output_path)
    #print("Image saved as "+output_path)
    #image.show()
