from flask import  request,jsonify
from flask import send_file
import base64
from pathlib import Path
from app.utils.logger import get_logger
from app.Services.IDReaderEndService import IDReaderEndService
logger = get_logger(__name__)

class IDReaderAPI_Mngr:
    """
    IDReaderAPI_Mngr is a class that manages the ID Reader API endpoints.
    It provides methods to handle requests related to ID reading and processing.
    """
    _iDReaderEndService_Mngr = IDReaderEndService("")
    def __new__(cls):
        raise TypeError("IDReaderAPI_Mngr is a static class and cannot be instantiated. Use the class name instead.")

    @staticmethod
    def process():
        logger.debug("Processing request in IDReaderAPI_Mngr")

        if 'image' not in request.files and 'image' not in request.form:
            return jsonify({"message": "No image provided"}), 400
        
        try:
            # Get image from form data
            if 'image' in request.files:
                file = request.files['image']
                ext = Path(file.filename).suffix.lower()
                # if ext not in ['.jpg', '.jpeg', '.png','.tiff','tif', '.bmp']:
                #     logger.error(f"Unsupported image format: {ext}. Supported formats are: .jpg, .jpeg, .png, .tiff, .bmp")
                #     return jsonify({"message": f"Unsupported image format: {ext}. Supported formats are: .jpg, .jpeg, .png, .tiff"}), 400
                img_bytes = file.read()
                logger.debug("Image Converted to bytes successfully")          
            else:
                # Handle base64 encoded image if needed
                logger.debug("Handling base64 encoded image")          
                img_bytes = base64.b64decode(request.form['image'].split(',')[1])
        except Exception as e:
            logger.error({"error": str(e)}, exc_info=True)
            return jsonify({"message": str(e)}), 500   
        
        logger.debug("Image bytes received successfully")
        try:
            logger.debug("Invoking IDReaderEndService for ID card readingon the image file %s",
                     file.filename if hasattr(file, 'filename') else '-- unknown --')
            extracted_data, processed_image = IDReaderAPI_Mngr._iDReaderEndService_Mngr.iDCardreader(img_bytes,ext)
        except Exception as e:
            logger.error(f"Error while extracting data: {str(e)}", exc_info=True)
            return jsonify({"message": str(e)}), 400
        
        logger.debug("ID Card Reader processing completed successfully")
        return jsonify({
            "processed_image": processed_image,
            "data": extracted_data
        })