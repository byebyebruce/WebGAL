import sys
import os
import io
from flask import Flask, request, send_file
import uuid
from workflow_api import ComfyUIClient

c = ComfyUIClient()
app = Flask(__name__)

@app.route('/remove_bg', methods=['POST'])
def api_remove_bg():
    """API模式处理接口"""
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {"error": "Empty filename"}, 400
    
    # 保存临时文件
    temp_path = f"/tmp/{uuid.uuid4()}.png"
    file.save(temp_path)
    
    try:
        img_data = c.process_image(temp_path)
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
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

def cli_mode(input_file):
    """命令行模式处理"""
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        sys.exit(1)
    
    try:
        output_path = "out.png"
        image_data = c.process_image(input_file)
        with open(output_path, 'wb') as f:
            f.write(image_data)
        # 重命名为out.png
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
