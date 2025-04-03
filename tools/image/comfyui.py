import websocket
import uuid
import json
import urllib.request
import urllib.parse
import requests
import os

class ComfyUIClient:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

    def upload_image_file(self, image_path):
        url = f"http://{self.server_address}/upload/image"
        with open(image_path, 'rb') as file:
            return self.upload_image(file)
            #files = {'image': (os.path.basename(image_path), file, 'image/png')}
            #data = {'overwrite': 'true'}
            #response = requests.post(url, files=files, data=data)
            #return response.json()

    def upload_image(self, image_data):
        url = f"http://{self.server_address}/upload/image"
        # Create a file-like object from image_data
        files = {'image': ('image.png', image_data, 'image/png')}
        data = {'overwrite': 'true'}
        response = requests.post(url, files=files, data=data)
        return response.json()
            
    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_history(self, prompt_id):
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())

    def get_images(self, ws, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        current_node = ""
        
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['prompt_id'] == prompt_id:
                        if data['node'] is None:
                            break  # 执行完成
                        else:
                            current_node = str(data['node'])  # 确保节点ID为字符串格式
            else:
                if current_node == '17':  # 对应SaveImageWebsocket节点ID
                    images_output = output_images.get(current_node, [])
                    images_output.append(out[8:])  # 去除8字节的头部信息
                    output_images[current_node] = images_output
        
        return output_images

    def process_image_file(self, input_path):
        with open(input_path, 'rb') as f:
            image_data = f.read()
        return self.process_image(image_data)

    def process_image(self, image_data):
        # 1. 上传图片到ComfyUI服务器
        upload_result = self.upload_image(image_data)
        filename = upload_result['name']  # 获取上传后的文件名

        # 2. 构建工作流Prompt
        prompt_text = f"""
        {{
        "1": {{
            "inputs": {{
            "image": "{filename}"
            }},
            "class_type": "LoadImage",
            "_meta": {{
            "title": "加载图像"
            }}
        }},
        "10": {{
            "inputs": {{
            "rmbgmodel": [
                "16",
                0
            ],
            "image": [
                "1",
                0
            ]
            }},
            "class_type": "BRIA_RMBG_Zho",
            "_meta": {{
            "title": "🧹BRIA RMBG"
            }}
        }},
        "16": {{
            "inputs": {{}},
            "class_type": "BRIA_RMBG_ModelLoader_Zho",
            "_meta": {{
            "title": "🧹BRIA_RMBG Model Loader"
            }}
        }},
        "17": {{
            "inputs": {{
            "images": [
                "10",
                0
            ]
            }},
            "class_type": "SaveImageWebsocket",
            "_meta": {{
            "title": "保存图像（网络接口）"
            }}
        }}
        }}
        """

        prompt = json.loads(prompt_text)

        # 3. 连接WebSocket并获取图片
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
        images = self.get_images(ws, prompt)
        ws.close()

        # 4. 处理返回的图片数据
        if '17' in images and len(images['17']) > 0:
            image_data = images['17'][0]
            return image_data

            # 保存图片到本地
            #with open(output_path, 'wb') as f:
            #    f.write(image_data)
            #print(f"处理后的图片已保存至：{output_path}")
            
            # 使用PIL显示图片（可选）
            # from PIL import Image
            # import io
            # image = Image.open(io.BytesIO(image_data))
            # image.show()
        else:
            print("未获取到处理后的图片")
