from flask import jsonify
import re
import json
from app.Services.OCRHandler import GeminiOCRreader
from app.utils.logger import get_logger
logger = get_logger(__name__)

class IDReaderEndService:
    _instance = None
    
    # This is a singleton class, ensuring only one instance exists
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IDReaderEndService, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    # This ensures that the service is a singleton and only initialized once
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            # Initialize the service only once
            # This ensures that the service is a singleton and only initialized once
            self._initialize_service()
    # This method is called to initialize the service
    def _initialize_service(self):
        # Perform any necessary initialization here
        # For example, setting up database connections, loading configurations, etc.
        print("IDReaderEndService initialized")
    # This method processes the request data
    def process_request(self, request_data):
        # Process the request data
        # This is a placeholder for actual processing logic
        print(f"Processing request data: {request_data}")
        return {"status": "success", "data": request_data}
    
    #----------------- Business Logic -----------------
    def iDCardreader(self,Imagefile):
        logger.debug("Starting ID Card Reader processing")
        if not Imagefile:
                raise ValueError("No image file provided")
        logger.info("Start Using OCRreader for OCR processing on the image file %s",
                     Imagefile.filename if hasattr(Imagefile, 'filename') else '-- unknown --')
        # try:
        #     ocrHandler = GeminiOCRreader(
        #         api_key=os.getenv('GOOGLE_API_KEY'),
        #         model=os.getenv('GOOGLE_OCR_MODEL', 'gemini-2.0-flash-001')
        #     )
        # except Exception as e:
        #     raise Exception(f"Error initializing OCR handler: {str(e)}")
        # try:
        #     data = ocrHandler.geminiOCRreader(Imagefile)
        # except Exception as e:
        #     raise Exception(f"Error processing image using the OCR Method: {str(e)}")
        try:
            data= GeminiOCRreader.geminiOCRreader(Imagefile)
        except Exception as e:
            raise Exception(f"Error processing image using the OCR Method: {str(e)}")
        if not data:
            raise ValueError("No data extracted from the image")
        
        logger.debug("OCR processing completed for image file: %s and Data extracted: %s",
                      Imagefile.filename if hasattr(Imagefile, 'filename') else '-- unknown --', data.text)
        # Extract JSON part from the OCR result
        match = re.search(r'\{.*\}', data.text, re.DOTALL)
        if match:
            json_part = match.group()
            logger.debug("Extracted JSON part: %s", json_part)
        else:
            logger.warning("No JSON part found in the OCR result")
        # Parse the JSON part
        data = IDReaderEndService.parse_json(json_part)

        # result = {
        #     'first_name': data.get('firstname', "N/A"),
        #     'second_name': data.get('parname', "N/A"),
        #     'full_name': f"{data.get('firstname', 'N/A')} {data.get('parname', 'N/A')}",
        #     'national_id': data.get('nationalID', "N/A"),
        #     'address': data.get('address', "N/A"),
        #     'birth': data.get('birthdate', "N/A"),
        #     'gov': data.get('gov', "N/A"),
        #     'gender': data.get('gender', "N/A"),
        # }
        return data
    
    @staticmethod
    def parse_json(json_string):
        try:
            # Attempt to parse the JSON string
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    def test_iDCardreader(self,Imagefile):
        logger.debug("Testing ID Card Reader with dummy data")
        type(Imagefile)
        logger.debug(f"Imagefile type: {type(Imagefile)}")
        if not Imagefile:
            raise ValueError("No image file provided")
        data= {}
        result = {
            'first_name': data.get('firstname', "Ahmed"),
            'second_name': data.get('parname', "Ali Ahmed"),
            'full_name': f"{data.get('firstname', 'Ahmed')} {data.get('parname', 'Ali Ahmed')}",
            'national_id': data.get('nationalID', "1223456"),
            'address': data.get('address', "AdressTest"),
            'birth': data.get('birthdate', "01/04/1151"),
            'gov': data.get('gov', "Giza"),
            'gender': data.get('gender', "Male"),
        }
        return result




