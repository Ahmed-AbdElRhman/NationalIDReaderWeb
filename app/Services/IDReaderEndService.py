import re
import os
from ultralytics import YOLO
import cv2
import numpy as np
import base64
import json
from app.Services.OCRHandler import GeminiOCRreader
from app.utils.logger import get_logger
from app.Database.dBService import OCRDB
# from run import app
logger = get_logger(__name__)


class IDReaderEndService:
    _instance = None
    DBService_Mngr = None
    # This is a singleton class, ensuring only one instance exists
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IDReaderEndService, cls).__new__(cls)
        return cls._instance
    
    # This ensures that the service is a singleton and only initialized once
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            # Initialize the DBService_Mngr if not already done
            self.DBService_Mngr = OCRDB()
            # Initialize the service only once
            # This ensures that the service is a singleton and only initialized once
            self._initialize_service()
    # This method is called to initialize the service

    def _initialize_service(self):
        # Perform any necessary initialization here
        print("IDReaderEndService initialized")
    # This method processes the request data

    #----------------- Business Logic -----------------
    # def iDCardreader(self,Imagefile,ext):
    #     logger.debug("HIIIIIIIIIIIIIII")
    #     self.DBService_Mngr.increment_scan_count()
    #     logger.debug("Total scans updated successfully in the database")
    #     return {},None
    
    def iDCardreader(self,Imagefile,ext,detectIDcard=False):
        logger.debug("Starting ID Card Reader processing")
        warningMSG=None
        if not Imagefile:
                raise ValueError("No image file provided")
        # Validate the subscription status
        logger.debug("Validating subscription status")
        is_valid, MSG = self.DBService_Mngr.validate_subscription()
        if not is_valid:
            logger.warning("Subscription validation failed: %s", MSG)
            raise ValueError(MSG)
        else:
            logger.debug("iDCardreaderORG::Subscription is valid")
            if MSG:
                logger.warning("Warning message: %s", MSG)
                warningMSG= MSG
        
        # Convert bytes to NumPy array
        nparr = np.frombuffer(Imagefile, np.uint8)
        # Decode into an OpenCV image (BGR format, same as cv2.imread)
        cv2Img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        logger.debug("Detecting ID card labels in the image file",)
        # read the ID card labels
        if detectIDcard:
            logger.debug("ID card detection is enabled, detecting and processing ID card in the image")
            try:
                processedImage=self._detect_and_process_id_card(cv2Img)
            except Exception as e:
                raise Exception(e)
        else:
            logger.debug("ID card detection is disabled, skipping ID card detection")
            processedImage=None
            # Convert to Base64 string processed_image
            # _, buffer = cv2.imencode(os.getenv('PROCESSED_IMAGE_TYPE','.jpg'), cv2Img)
            # processedImage = base64.b64encode(buffer).decode('utf-8')
        # Perform OCR processing on the image file using GeminiOCRreader
        logger.debug("Start OCR extraction Process")
        ocrResults= self._OCRMethod(Imagefile,ext)
        logger.debug("OCR Results type: %s", type(ocrResults))
        logger.debug("OCR results: %s", ocrResults)
        nationalID=ocrResults["NationalID"].get('english')
        if not nationalID:
            raise ValueError("No national ID number found in the OCR results:%s", ocrResults)
        # Decode the Egyptian national ID
        logger.debug("Decoding Egyptian national ID")
        ocrResults.update(self._decode_egyptian_id(nationalID))
        logger.debug("Full Decoded ID information: %s", ocrResults)
        logger.debug("ID card Process completed successfully")
        # Udate the subscription total scans in the database
        updated, errorMSG = self.DBService_Mngr.increment_scan_count()
        if not updated:
            raise Exception(f"Error updating scan count in the database: {errorMSG}")
        logger.debug("Total scans updated successfully in the database")
        return ocrResults,processedImage,warningMSG
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
        logger.debug("Detecting ID card Lebels in the image...")
        # Load the ID card detection model
        id_card_model = YOLO('app\Services\models\detect_id_card.pt')
        # Perform inference to detect the ID card
        id_card_results = id_card_model(image)
        # Check if any ID card was detected
        if not id_card_results or not id_card_results[0].boxes:
            raise ValueError("No ID card detected in the image")
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
            '01': {"arabic": "القاهرة", "english": "Cairo"},
            '02': {"arabic": "الإسكندرية", "english": "Alexandria"},
            '03': {"arabic": "بورسعيد", "english": "Port Said"},
            '04': {"arabic": "السويس", "english": "Suez"},
            '11': {"arabic": "دمياط", "english": "Damietta"},
            '12': {"arabic": "الدقهلية", "english": "Dakahlia"},
            '13': {"arabic": "الشرقية", "english": "Ash Sharqia"},
            '14': {"arabic": "القليوبية", "english": "Kaliobeya"},
            '15': {"arabic": "كفر الشيخ", "english": "Kafr El-Sheikh"},
            '16': {"arabic": "الغربية", "english": "Gharbia"},
            '17': {"arabic": "المنوفية", "english": "Monoufia"},
            '18': {"arabic": "البحيرة", "english": "El Beheira"},
            '19': {"arabic": "الإسماعيلية", "english": "Ismailia"},
            '21': {"arabic": "الجيزة", "english": "Giza"},
            '22': {"arabic": "بني سويف", "english": "Beni Suef"},
            '23': {"arabic": "الفيوم", "english": "Fayoum"},
            '24': {"arabic": "المنيا", "english": "El Minya"},
            '25': {"arabic": "أسيوط", "english": "Assiut"},
            '26': {"arabic": "سوهاج", "english": "Sohag"},
            '27': {"arabic": "قنا", "english": "Qena"},
            '28': {"arabic": "أسوان", "english": "Aswan"},
            '29': {"arabic": "الأقصر", "english": "Luxor"},
            '31': {"arabic": "البحر الأحمر", "english": "Red Sea"},
            '32': {"arabic": "الوادي الجديد", "english": "New Valley"},
            '33': {"arabic": "مطروح", "english": "Matrouh"},
            '34': {"arabic": "شمال سيناء", "english": "North Sinai"},
            '35': {"arabic": "جنوب سيناء", "english": "South Sinai"},
            '88': {"arabic": "أجنبي", "english": "Foreign"}
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

        if gender_code % 2 != 0:  # Odd → Male
            gender = {"arabic": "ذكر", "english": "Male"}
        else:  # Even → Female
            gender = {"arabic": "أنثى", "english": "Female"}

        governorate = governorates.get(governorate_code, {"arabic": "غير معروف", "english": "Unknown"})
        birth_date_en = f"{full_year:04d}/{month:02d}/{day:02d}"
        # English → Arabic digit mapping
        en_to_ar = {
            "0": "٠", "1": "١", "2": "٢", "3": "٣", "4": "٤",
            "5": "٥", "6": "٦", "7": "٧", "8": "٨", "9": "٩"
        }
        birth_date_ar = "".join(en_to_ar[ch] if ch.isdigit() else ch for ch in birth_date_en)
        return {
            'birth': {'arabic':birth_date_ar , 'english': birth_date_en},
            'gov': governorate,
            'gender': gender
        }
    def _parse_json(self,json_string):
        try:
            # Attempt to parse the JSON string
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f'Error decoding JSON: {str(e)}')
    def get_subscription_status(self):
        """
        Retrieves the current subscription status from the database.
        """
        logger.debug("Retrieving subscription status")
        subscriptionDict = self.DBService_Mngr.get_subscription_status()

        if not subscriptionDict:
            raise ValueError("No subscription found in the database")
        return subscriptionDict
    # ---------------- User Authentication ----------------
    def validate_user_credentials(self, username, password):
        logger.debug("Login method called with username: %s", username)
        adminusr = self.DBService_Mngr.login_admin_user(username, password)
        if adminusr:
            logger.debug("Login successful for user: %s", username)
            return adminusr
        else:
            logger.warning("Login failed for user: %s", username)
            raise ValueError("Invalid username or password")
    # ---------------- Update Admin User ----------------
    def update_admin_password(self,username,currentpassword,new_password):
        logger.debug("Upadete User Password: %s", new_password)
        if self.DBService_Mngr.update_admin_password(username,currentpassword,new_password):
            logger.warning("user Updated successful")
            return True
        else:
            logger.warning("Unable to Update the user Password")
            raise ValueError("Invalid username or Password")
    # ---------------- Subscription ReNew ----------------
    def reNew_Subscriptiobn(self,MAX_SCANS,subscription_expiry_days):
       logger.debug("Renew the Subscription Process")
       subscription = self.DBService_Mngr.renew_subscription(MAX_SCANS,subscription_expiry_days)
       if subscription:
           logger.debug("Subscription Renewed")
           return subscription
       else:
           logger.debug("Unable to Renewed the Subscription")
           return None
       
