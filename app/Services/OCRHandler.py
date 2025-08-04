from google import genai
from google.genai import types
from pathlib import Path
from app.utils.logger import get_logger
logger = get_logger(__name__)
from dotenv import load_dotenv
import os
load_dotenv()

class GeminiOCRreader:
    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
    model = os.getenv('GOOGLE_OCR_MODEL', 'gemini-2.0-flash-001')
    # This method processes the image file using the Gemini OCR model.
    @staticmethod
    def geminiOCRreader(imageFile):
        """ Processes the image file using the Gemini OCR model.
        Args:
            imageFile (str): The path to the image file to be processed.
        Returns:
            response: The response from the Gemini OCR model containing extracted data.
        """
        logger.debug("Starting Gemini OCR Upload for image file: %s", imageFile.filename if hasattr(imageFile, 'filename') else '-- unknown --')
        # file = GeminiOCRreader.client.files.upload(file=imageFile)
        logger.debug("Starting Gemini OCR Processing for image file: %s", imageFile.filename if hasattr(imageFile, 'filename') else '-- unknown --')

        ext = Path(imageFile.filename).suffix.lower()
        if ext not in ['.jpg', '.jpeg', '.png','.tiff']:
            raise ValueError(f"Unsupported image format: {ext}. Supported formats are: .jpg, .jpeg, .png, .tiff")
        # Read the image file and convert it to bytes
        image_bytes = imageFile.read()
        image = types.Part.from_bytes(
        data=image_bytes, mime_type="image/"+ext.lstrip('.') if ext else "image/jpg"  # Default to jpg if no extension is provided
        )
        client = GeminiOCRreader.client
        response = client.models.generate_content(
            model=GeminiOCRreader.model,
            contents=['This is an Arabic National ID card, which contains the his name,parent full name,adress, national ID (Arabic numbers), and other data. Act as a highly accurate and specialized Arabic Optical Character Recognition (OCR) system, so please extract all Arabic characters/numbers from the image, be proficient in interpreting Arabic National ID cards, and send the response as a fixed JSON form containing {firstname:"",parname:"",address:"",nationalID:"}. You can also predict the word that was not read correctly.make it fast an acurate and make sure to return all data in english',
                       image],
        )
        # response = GeminiOCRreader.client.models.generate_content(
        # model=GeminiOCRreader.model,
        #     contents=[ 
        #         types.Part.from_bytes
        #             (
        #                 data=imageFile,mime_type="image/jpg"
        #             ),
        #         'This is an Arabic National ID card, which contains the his name,parent full name,adress, national ID (Arabic numbers), and other data. Act as a highly accurate and specialized Arabic Optical Character Recognition (OCR) system, so please extract all Arabic characters/numbers from the image, be proficient in interpreting Arabic National ID cards, and send the response as a fixed JSON form containing {firstname:"",parname:"",address:"",nationalID:"}. You can also predict the word that was not read correctly.make it fast an acurate and make sure to return all data in english'
        #             ]
        # )
        logger.debug("Gemini OCR Processing completed for image file: %s", imageFile.filename if hasattr(imageFile, 'filename') else '-- unknown --')
        logger.debug("Response from Gemini OCR: %s for image file: %s", response, imageFile.filename if hasattr(imageFile, 'filename') else '-- unknown --')
        return response