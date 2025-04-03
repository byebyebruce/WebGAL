import os
import requests
import time
from dotenv import load_dotenv

class SilliconClient:
    def __init__(self, api_key=""):
        """
        Initialize the ImageGenerator with an API token
        
        Args:
            token (str): API authorization token
        """
        if api_key == "":
            load_dotenv()
            self.api_key = os.getenv("SILLICONFLOW_API_KEY")
        else:
            self.api_key = api_key
        self.url = "https://api.siliconflow.cn/v1/images/generations"
        
	# image_size = 2048x1125,768x1024,1536x2048,1024x2048, 1024x1024, 960x1280, 768x1024, 720x1440, 720x1280)
    def generate_image(self, prompt, negative_prompt="", image_size="2048x1125", 
                      batch_size=1, seed=0, num_inference_steps=20, 
                      guidance_scale=7.5):
        """
        Generate an image using the Kolors API and return the first generated image URL
        
        Args:
            prompt (str): The description of the image to generate
            negative_prompt (str): Negative prompt for generation
            image_size (str): Size of the output image
            batch_size (int): Number of images to generate
            seed (int): Random seed for generation
            num_inference_steps (int): Number of inference steps
            guidance_scale (float): Guidance scale for generation
            base64_image (str): Base64 encoded image string
            
        Returns:
            str: URL of the first generated image
        """
        payload = {
            "model": "Kwai-Kolors/Kolors",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_size": image_size,
            "batch_size": batch_size,
            "seed": seed,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            #"image": f"data:image/webp;base64, {base64_image}"
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", self.url, json=payload, headers=headers)
        response.raise_for_status()
        
        """
        Example response format:
        {
        "images": [
            {
            "url": "<string>"
            }
        ],
        "timings": {
            "inference": 123
        },
        "seed": 123
        }
        """
        response_data = response.json()
        # Return the URL of the first generated image
        image_url = response_data["images"][0]["url"]

        print(image_url)
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception("Failed to download image")
            
        # Return the image data directly
        return response.content

if __name__ == "__main__":
    import sys

    prompt = """A Studio Ghibli-inspired illustration featuring a teenage girl with an expressive, angry demeanor. She is depicted in a frontal half-body view, with her brows furrowed and her mouth slightly open in frustration. Her hair is styled in a natural, flowing manner, perhaps with a few loose strands framing her face. She wears a simple yet charming outfit reminiscent of Ghibli characters, with earthy colors and a touch of whimsy.

The background is soft and dreamy, with hints of nature, like trees or flowers, to evoke the enchanting atmosphere typical of Ghibli films. The color palette is warm and inviting, capturing the essence of hand-drawn animation. Her expression is powerful yet relatable, embodying the spirit of youthful emotion in a way that feels both genuine and magical.
"""
    output_path = "output.png"
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    print("prompt:"+prompt)

    generator = SilliconClient()
    image_data = generator.generate_image(prompt,image_size="768x1024")
    with open(output_path, "wb") as f:
        f.write(image_data)
        print("output_path:"+output_path)