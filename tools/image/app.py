import sys
import os
import io
from flask import Flask, request, send_file
import uuid
from comfyui import ComfyUIClient
from sillicon import SilliconClient
from gemini import GeminiClient
from dotenv import load_dotenv

load_dotenv()
sillicon = SilliconClient(os.getenv("SILLICONFLOW_API_KEY"))
gemini = GeminiClient(os.getenv("GEMINI_API_KEY"))
comfyui = ComfyUIClient()
app = Flask(__name__)

@app.route('/gen_image', methods=['POST'])
def api_gen_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        negative_prompt = data.get('negative_prompt', '')
        image_size = data.get('image_size', '2048x1125')
        #batch_size = int(data.get('batch_size', 1))
        rmbg = data.get('rmbg', False)

        image_data = sillicon.generate_image(
            prompt,
            negative_prompt = negative_prompt,
            image_size = image_size,
            #batch_size = batch_size
        )
        if rmbg:
            image_data = comfyui.process_image(image_data)

        img_io = io.BytesIO(image_data)
        # Ensure pointer is at start of buffer
        img_io.seek(0)
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False,  # Changed to False to allow direct viewing
            download_name='output.png'
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        # 打印堆栈信息
        import traceback
        traceback.print_exc()

        return {"error": str(e)}, 500

@app.route('/edit_image', methods=['POST'])
def api_edit_image():
    try:
        # Check for file upload
        if 'file' not in request.files:
            return {"error": "No file uploaded"}, 400
        file = request.files['file']
        if file.filename == '':
            return {"error": "Empty filename"}, 400
         # 将 FileStorage 对象转换为字节对象
        file_bytes = file.read()
        file.seek(0) 
            
        # Get form data parameters
        prompt = request.form.get('prompt')
        rmbg = request.form.get('rmbg', 'false').lower() == 'true'
        
        if not prompt:
            return {"error": "No prompt provided"}, 400
            
        # Process image with Gemini
        image_data = gemini.generate_image(prompt, file_bytes)
        
        # Remove background if requested
        if rmbg:
            image_data = comfyui.process_image(image_data)

        img_io = io.BytesIO(image_data)
        # Ensure pointer is at start of buffer
        img_io.seek(0)
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False,  # Changed to False to allow direct viewing
            download_name='output.png'
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        # 打印堆栈信息
        import traceback
        traceback.print_exc()

        return {"error": str(e)}, 500

@app.route('/remove_bg', methods=['POST'])
def api_remove_bg():
    """API模式处理接口"""
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {"error": "Empty filename"}, 400
    
    # 保存临时文件
    #temp_path = f"/tmp/{uuid.uuid4()}.png"
    #file.save(temp_path)
    
    try:
        img_data = comfyui.process_image(file)
        # Create a BytesIO object from the image data
        img_io = io.BytesIO(img_data)
        # Ensure pointer is at start of buffer
        img_io.seek(0)
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False,  # Changed to False to allow direct viewing
            download_name='output.png'
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}, 500
    #finally:
        # 清理临时文件
        #if os.path.exists(temp_path):
        #    os.remove(temp_path)
        #if 'output_path' in locals() and os.path.exists(output_path):
        #    os.remove(output_path)

def cli_mode(prompt, rmbg=True):
    try:
        image_data = sillicon.generate_image(
            prompt,
        )
        if rmbg:
            image_data = c.process_image(image_data)
        with open("out.png", 'wb') as f:
            f.write(image_data)
        #os.rename(output_path, "out.png")
        print("Processing completed. Output saved to out.png")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # 命令行参数解析
    if len(sys.argv) == 2:  # 命令行模式
        cli_mode(sys.argv[1])
    elif len(sys.argv) == 1:  # API模式
        app.run(host='0.0.0.0', port=5100)
    else:
        print("Usage:")
        print("  API模式: python3 workflow_api.py")
        print("  CLI模式: python3 workflow_api.py input.png")
        sys.exit(1)
