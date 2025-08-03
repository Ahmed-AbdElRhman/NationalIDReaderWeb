from flask import Flask, render_template, request, jsonify, send_file
import os
import win32com.client
import pythoncom
from werkzeug.utils import secure_filename
from app.Services.OCRHandler import OCRHandler
# from .utils.logging_config import configure_logging
import utils
import utils.logging_config
import logging

app = Flask(__name__,template_folder='Front/templates', static_folder='Front/static')
app.config['JSON_AS_ASCII'] = False  # To handle non-ASCII characters in JSON responses
utils.logging_config.configure_logging(app)
# Define the upload folder path
UPLOAD_FOLDER = os.path.join(os.getcwd(), "Front/uploads")
print(f"Upload folder: {UPLOAD_FOLDER}")
# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    print(f"Creating upload folder: {UPLOAD_FOLDER}")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)



def list_scanners():
    scannerlist_device = []
    scannerlist_device.clear()
    pythoncom.CoInitialize()
    wia = win32com.client.Dispatch("WIA.DeviceManager")
    scannerNames = []
    for device in wia.DeviceInfos:
        if device.Type == 1:  # Scanner
            scannerNames.append(device.Properties['Name'].Value)
            scannerlist_device.append({'name': device.Properties['Name'].Value, 'device': device})
    return scannerNames

def scan(scanner_OBJ):
    scanner = scanner_OBJ.Connect()
    item = scanner.Items[0]
    img = item.Transfer(FormatID="{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}")  # WIA FormatJPEG
    output_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, "scanned_image.jpg"))
    if os.path.exists(output_path):
        os.remove(output_path)
    img.SaveFile(output_path)
    return output_path

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/list_scanners")
def api_list_scanners():
    scanners = list_scanners()
    return jsonify(scanners)

@app.route("/scan", methods=["POST"])
def api_scan():
    scanner_name = request.form.get("scanner_name")
    if not scanner_name:
        return jsonify({"error": "No scanner specified"}), 400
    image_path = scan(scanner_name)
    return jsonify({"image_path": image_path})

@app.route("/process", methods=["POST"])
def api_process():
    ocrHandler = OCRHandler()
    logger = logging.getLogger(__name__)
    print(f"Hiiiiiiiiiiiiiiiii")
    logger.info("Hiiiiiiiiiiiiiiiiiiiiiiiiiiiii iDReader here")
    data = ocrHandler.iDReader("")
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    ocrHandler = OCRHandler()
    print(f"Hiiiiiiiiiiiiiiiii")
    data = ocrHandler.iDReader(filepath)

    result = {
        'first_name': data.get('firstname', "N/A"),
        'second_name': data.get('parname', "N/A"),
        'full_name': f"{data.get('firstname', 'N/A')} {data.get('parname', 'N/A')}",
        'national_id': data.get('nationalID', "N/A"),
        'address': data.get('address', "N/A"),
        'birth': data.get('birthdate', "N/A"),
        'gov': data.get('gov', "N/A"),
        'gender': data.get('gender', "N/A"),
    }
    return jsonify(result)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == "__main__":
    app.run(debug=True)
