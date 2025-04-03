import os
import requests
import time
from dotenv import load_dotenv

negative_prompt = """nsfw, paintings, cartoon, anime, sketches, worst quality, low quality, normal quality, lowres, watermark, monochrome, grayscale, ugly, blurry, Tan skin, dark skin, black skin, skin spots, skin blemishes, age spot, glans, disabled, distorted, bad anatomy, morbid, malformation, amputation, bad proportions, twins, missing body, fused body, extra head, poorly drawn face, bad eyes, deformed eye, unclear eyes, cross-eyed, long neck, malformed limbs, extra limbs, extra arms, missing arms, bad tongue, strange fingers, mutated hands, missing hands, poorly drawn hands, extra hands, fused hands, connected hand, bad hands, wrong fingers, missing fingers, extra fingers, 4 fingers, 3 fingers, deformed hands, extra legs, bad legs, many legs, more than two legs, bad feet, wrong feet, extra feets"""
class SilliconClient:
    def __init__(self, api_key=""):
        """
        Initialize the ImageGenerator with an API token
        
        Args:
            token (str): API authorization token
        """
        if api_key == "":
            load_dotenv(override=True)
            self.api_key = os.getenv("SILLICONFLOW_API_KEY")
        else:
            self.api_key = api_key
        #self.url = "https://api.siliconflow.cn/v1/images/generations"
        
	# image_size = 2048x1125,768x1024,1536x2048,1024x2048, 1024x1024, 960x1280, 768x1024, 720x1440, 720x1280)
    def generate_image(self, prompt, negative_prompt=negative_prompt, image_size="2048x1125", 
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

        url = "https://api.siliconflow.cn/v1/images/generations"
        response = requests.request("POST", url, json=payload, headers=headers)
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


    def chat_completion(self,user_prompt, sys_prompt="", model="Qwen/Qwen2.5-32B-Instruct", stream=False, 
                       max_tokens=4096, stop=None, temperature=0.7, top_p=0.7,
                       top_k=50, frequency_penalty=0.5, n=1):
        """
        Send a chat completion request to the API
        
        Args:
            message (str): The message to send
            model (str): Model to use
            stream (bool): Whether to stream the response
            max_tokens (int): Maximum tokens to generate
            stop (str): Stop sequence
            temperature (float): Sampling temperature
            top_p (float): Top p sampling parameter
            top_k (int): Top k sampling parameter
            frequency_penalty (float): Frequency penalty
            n (int): Number of completions to generate
            
        Returns:
            dict: API response data
        """
        payload = {
            "model": model,
            "messages": [],
            "stream": stream,
            "max_tokens": max_tokens,
            "stop": stop,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "frequency_penalty": frequency_penalty,
            "n": n,
            "response_format": {"type": "text"},
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "description": "<string>",
                        "name": "<string>",
                        "parameters": {},
                        "strict": False
                    }
                }
            ]
        }
        
        if sys_prompt:
            payload["messages"].append({
                "role": "system",
                "content": sys_prompt
            })
            
        payload["messages"].append({
            "role": "user", 
            "content": user_prompt
        })

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        url = "https://api.siliconflow.cn/v1/chat/completions"
        response = requests.request("POST", url, json=payload, headers=headers)
        response.raise_for_status()
        
        resp = response.json()
        #print(resp)
        # Access dictionary keys properly for the response structure
        return resp['choices'][0]['message']['content']

if __name__ == "__main__":
    import sys
    act = sys.argv[1]
    if act == "chat":
        client = SilliconClient()
        if len(sys.argv) == 3:
            resp = client.chat_completion(sys.argv[2])
            print(resp)
        elif len(sys.argv) > 3:
            resp = client.chat_completion(sys.argv[2],sys.argv[3])
            print(resp)
        else :
            print("Usage: python3 "+sys.argv[0]+" chat <prompt> <sys_prompt>") 
        sys.exit(0)
    if act == "image":
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