from flask import  request,jsonify
from app.utils.logger import get_logger
from app.Services.IDReaderEndService import IDReaderEndService
logger = get_logger(__name__)

class IDReaderAPI_Mngr:
    """
    IDReaderAPI_Mngr is a class that manages the ID Reader API endpoints.
    It provides methods to handle requests related to ID reading and processing.
    """
    _iDReaderEndService_Mngr = IDReaderEndService()
    def __new__(cls):
        raise TypeError("IDReaderAPI_Mngr is a static class and cannot be instantiated. Use the class name instead.")

    @staticmethod
    def process():
        logger.debug("Processing request in IDReaderAPI_Mngr")
        imageFile = request.files.get("idImage")
        imageExtention = imageFile.content_type
        print(f"Image file extension: {imageExtention}")
        if not imageFile:
            return jsonify({"error": "No file uploaded"}), 400
        logger.debug("Received file: %s", imageFile.filename)

        #
        # OCR Extraction
        try:
            data = IDReaderAPI_Mngr._iDReaderEndService_Mngr.iDCardreader(imageFile)
        except Exception as e:
            logger.error(f"Error processing ID card: {str(e)}")
            return jsonify({"Error processing ID card": str(e)}), 500
        logger.debug("data received from IDReaderEndService_Mngr: %s", data)
        return jsonify(data)
