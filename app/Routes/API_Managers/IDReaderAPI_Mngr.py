from flask import  request,jsonify
# from flask import send_file
from flask import session
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
    _iDReaderEndService_Mngr = IDReaderEndService()
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
            extracted_data, processed_image,warningMSG = IDReaderAPI_Mngr._iDReaderEndService_Mngr.iDCardreader(img_bytes,ext)
        except Exception as e:
            logger.error(f"Error while extracting data: {str(e)}", exc_info=True)
            return jsonify({"message": str(e)}), 400
        
        logger.debug("ID Card Reader processing completed successfully")
        return jsonify({
            "processed_image": processed_image,
            "data": extracted_data,
            "warning": warningMSG
        })
    @staticmethod
    def login():
        """
        Handles the login request.
        """
        logger.debug("Processing login request")
        data = request.form
        logger.debug("Hiiiiiiiiiiiii data: %s", data['username'])
        if not data or 'username' not in data or 'password' not in data:
            logger.error("Invalid login request: Missing username or password")
            return jsonify({"message": "Username and password are required"}), 400
        username = data['username']
        password = data['password']
        
        # Check the username and password against a database
        try:
            logger.debug("Validating user credentials for username: %s", username)
            IDReaderAPI_Mngr._iDReaderEndService_Mngr.validate_user_credentials(username, password)
            # get current Subscription status
            # logger.debug("Fetching subscription status for user: %s", username)
            # data = IDReaderAPI_Mngr._iDReaderEndService_Mngr.get_subscription_status()
            session['login']= True
            return jsonify({
                "message": "Login successful",
            }), 200
        except ValueError as e:
            logger.error("Login failed: %s", str(e))
            return jsonify({"message": str(e)}), 401
    @staticmethod
    def get_subscription_status():
        """
        Retrieves the subscription status for the user.
        """
        logger.debug("Fetching subscription status")
        try:
            data = IDReaderAPI_Mngr._iDReaderEndService_Mngr.get_subscription_status()
            logger.debug("Subscription status Data fetched successfully: %s", data)
            return jsonify({
                "data": data,
            }), 200
        except Exception as e:
            logger.error("Error fetching subscription status: %s", str(e))
            return jsonify({"message": str(e)}), 500
    @staticmethod
    def logout():
        """
        Handles the logout request.
        """
        logger.debug("Processing logout request")
        session.clear()
        return jsonify({"message": "Logout successful"}), 200
    
    @staticmethod
    def reNew_Subscriptiobn():
        """
        Handles the Subscription Renew Request.
        """
        subscription = IDReaderAPI_Mngr._iDReaderEndService_Mngr.reNew_Subscriptiobn()
        if subscription:
            logger.debug("Subscription Renewed")
            return jsonify({"message": "Subscription Renewed"}), 200
        else:
            logger.error("Error unable tot renew the subscription")
            return jsonify({"message": "Error unable tot renew the subscription"}), 500
       