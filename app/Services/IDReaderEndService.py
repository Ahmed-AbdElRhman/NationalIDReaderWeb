import re
import os
from ultralytics import YOLO
import cv2
import numpy as np
import base64
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
    # ---------------- ID Card Reader ----------------
    def iDCardreader(self,Imagefile,ext):
        logger.debug("Starting ID Card Reader processing")
        if not Imagefile:
                raise ValueError("No image file provided")

        # Convert bytes to NumPy array
        nparr = np.frombuffer(Imagefile, np.uint8)
        # Decode into an OpenCV image (BGR format, same as cv2.imread)
        cv2Img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        logger.debug("Detecting ID card labels in the image file",)
        # read the ID card labels
        try:
            processedImage=self._detect_and_process_id_card(cv2Img)
        except Exception as e:
            raise Exception(f"Error While reading the ID card labels in the image: {str(e)}")
        # Perform OCR processing on the image file using GeminiOCRreader
        logger.debug("Start OCR extraction Process")
        ocrResults= self._OCRMethod(Imagefile,ext)
        logger.debug("OCR results: %s", ocrResults)
        logger.debug("ID card Process completed successfully")
        return ocrResults,processedImage
    # ---------------- OCR Method ----------------
    def _OCRMethod(self, img_bytes,ext):
        try:
            OCRResult= GeminiOCRreader.geminiOCRreader(img_bytes,ext)
            logger.debug("OCR Result Type: %s", type(OCRResult))
        except Exception as e:
            raise Exception(f"Error processing image using the OCR Method: {str(e)}")
        if not OCRResult:
            raise ValueError("No data extracted from the image")
        
        match = re.search(r'\{.*\}', OCRResult, re.DOTALL)
        if match:
            json_part = match.group()
            logger.debug("JSON part extracted from OCR result: %s",json_part)
        else:
            raise ValueError("No JSON data found in the OCR result")
        return self._parse_json(json_part)
    # ---------------- ID label detection and processing ----------------
    def _detect_and_process_id_card(self, image):
        print("Detecting ID card...")
        # Load the ID card detection model
        id_card_model = YOLO('app\Services\models\detect_id_card.pt')
        # Perform inference to detect the ID card
        id_card_results = id_card_model(image)
        # Crop the ID card from the image
        for result in id_card_results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get bounding box coordinates
                cropped_image = image[y1:y2, x1:x2]
        # Pass the cropped image to the existing processing function
        model = YOLO('app\Services\models\detect_odjects.pt')
        results = model(cropped_image)
        annotated_img = results[0].plot()
        # Convert to Base64 string processed_image
        _, buffer = cv2.imencode(os.getenv('PROCESSED_IMAGE_TYPE','.jpg'), annotated_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return img_base64
    # ---------------- National ID Decoder ----------------
    def _decode_egyptian_id(self, id_number):
        governorates = {
            '01': 'Cairo',
            '02': 'Alexandria',
            '03': 'Port Said',
            '04': 'Suez',
            '11': 'Damietta',
            '12': 'Dakahlia',
            '13': 'Ash Sharqia',
            '14': 'Kaliobeya',
            '15': 'Kafr El - Sheikh',
            '16': 'Gharbia',
            '17': 'Monoufia',
            '18': 'El Beheira',
            '19': 'Ismailia',
            '21': 'Giza',
            '22': 'Beni Suef',
            '23': 'Fayoum',
            '24': 'El Menia',
            '25': 'Assiut',
            '26': 'Sohag',
            '27': 'Qena',
            '28': 'Aswan',
            '29': 'Luxor',
            '31': 'Red Sea',
            '32': 'New Valley',
            '33': 'Matrouh',
            '34': 'North Sinai',
            '35': 'South Sinai',
            '88': 'Foreign'
        }

        century_digit = int(id_number[0])
        year = int(id_number[1:3])
        month = int(id_number[3:5])
        day = int(id_number[5:7])
        governorate_code = id_number[7:9]
        gender_code = int(id_number[12:13])

        if century_digit == 2:
            century = "1900-1999"
            full_year = 1900 + year
        elif century_digit == 3:
            century = "2000-2099"
            full_year = 2000 + year
        else:
            raise ValueError("Invalid century digit")

        gender = "Male" if gender_code % 2 != 0 else "Female"
        governorate = governorates.get(governorate_code, "Unknown")
        birth_date = f"{full_year:04d}-{month:02d}-{day:02d}"

        return {
            'Birth Date': birth_date,
            'Governorate': governorate,
            'Gender': gender
        }
    def _parse_json(self,json_string):
        try:
            # Attempt to parse the JSON string
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f'Error decoding JSON: {str(e)}')
        
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