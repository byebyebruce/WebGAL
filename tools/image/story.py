import sys
import os
import io
import uuid
from comfyui import ComfyUIClient
from sillicon import SilliconClient
from gemini import GeminiClient
from dotenv import load_dotenv
import time

fix_figure_prompt = """Fix this image by correcting the facial features, hands, and any incorrect facial details. The face should be clear, and the body should be harmonious."""
expression_desc = {
    "speak_1":"Change the facial expression to one with the mouth open, as if about to speak.",
    "speak_2":"Change the facial expression to a closed mouth and closed eyes.",
    #"speak_3":"Change the facial expression to a pursed mouth.",
    "smile": "Change the expression to a happy smile with the corners of the mouth turned up.",
    #"laugh": "Change the expression to a wide-open mouth with a hearty laugh.",
    "sad": "Change the expression to sadness, with tears in the eyes.",
    "angry": "Change the expression to very angry, with furrowed brows.",
    #"surprise": "Change the expression to surprise, with the mouth wide open.",
    #"fear": "Change the expression to sheer terror, looking frightened and anxious.",
}

gen_img_prompt = """你是图片生成提示词助手，你根据用户的描述来丰富和完善用来生成图片的提示词。

生成提示词时参考下面几个：
A stunning and vibrant 3D render scene featuring a decadent chocolate strawberry cake with the number '4000' displayed byluxurious candles. The cake is beautifully adorned with colorful confetti, dripping frosting, and a sparkly red ribbon. Surrounding the cake are floating candles, thumbs up icons, and red neon hearts. Iconic superheroes such as Hulk, Spider-Man, Batman, Captain America, and Superman are seen celebrating the momentous occasion. The bold, glowing words 'followers Thank you ideogramers!' are written on the cake, indicating a celebration of a significant milestone among social media followers. The image bears the red neon firm signature "Hans Darias AI" and is captured in a cinematic, fashionable style., photo, cinematic, fashionLess

A British shorthair kitten, dressed in a tracksuit, stands on its hind legs at an airport, looking up curiously at the departure board. The kitten is wearing a mini backpack and a travel hat, with a small suitcase placed beside it. The scene is bustling, with passengers moving around and background announcements being broadcast. The kitten is personified, depicted in a cinematic style with lifelike photo effects

Peach and water photography, light pink background, surreal still life photography, macro shot tropical fruits, translucent textures, rendered in zbrush style, anime aesthetic, fairy tale core, sparkling water droplets, specular reflection, gorgeous colors, 8k

你必须用英文回复。你只回复提示词，不要回复其他任何内容。"""
class Story:
    def __init__(self):
        load_dotenv()
        self.comfyui = ComfyUIClient()
        self.sillicon = SilliconClient()
        self.gemini = GeminiClient()

    def generate_img(self, prompt, rmbg=False,image_size="1024x1024"):
        # 优化提示词
        new_prompt = self.sillicon.chat_completion(prompt,sys_prompt=gen_img_prompt)
        print("new_prompt:"+new_prompt)
        # 生成图片
        image_data = self.sillicon.generate_image(prompt,image_size=image_size)
        if rmbg:
            image_data = self.comfyui.process_image(image_data)
        return image_data
    
    def edit_figure_image(self,image_data, prompt, rmbg=True):
        image_data = self.gemini.generate_image(prompt,image_bytes=image_data)
        if rmbg:
            image_data = self.comfyui.process_image(image_data)
        return image_data


if __name__ == "__main__":
    story = Story()
    act = sys.argv[1]
    prompt = ""
    if act=="figure":
        if len(sys.argv) > 2:
            prompt = sys.argv[2]
            image_bytes = story.generate_img(prompt, image_size="768x1024" )
            with open("story.png", 'wb') as f:
                f.write(image_bytes)
                print("Processing completed. Output saved to story.png")
        else :
            with open("story.png", 'rb') as f:
                image_bytes = f.read()
        """
        image_bytes = story.edit_figure_image(image_bytes,fix_figure_prompt, rmbg=False)
        with open("story_fix.png", 'wb') as f:
            f.write(image_bytes)
            print("Processing completed. Output saved to story_fix.png")
        """

        for k,v in expression_desc.items():
            image_bytes = story.edit_figure_image(image_bytes,v)
            # Wait for 300ms before proceeding
            time.sleep(0.3)
            outpath = "story_"+k+".png"
            with open(outpath, 'wb') as f:
                f.write(image_bytes)
                print("Processing completed. Output saved to :",outpath)
    elif act=="scene":
        prompt = sys.argv[2]
        outpath = "scene.png"
        image_bytes = story.generate_img(prompt, image_size="2048x1125")
        if len(sys.argv) > 3:
            outpath = sys.argv[3]
        with open(outpath, 'wb') as f:
            f.write(image_bytes)
            print("Processing completed. Output saved to story.png")
    else:
        print("act not found")
