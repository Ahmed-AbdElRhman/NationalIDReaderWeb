from google import genai
from google.genai import types
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
    # def geminiOCRreader(imageFile):
    #     # Simulating a response for testing purposes
    #     response = {
    #                 "text":"""```json
    #                 {
    #                 "firstname": "Nihad Mohamed",
    #                 "parname": "Sediq Elshourbagy",
    #                 "address": "building 17 military residencies, Awal el Salam - Cairo",
    #                 "nationalID": "29602060101417"
    #                 }
    #                 ```"""
    #                 }
    #     logger.debug("Simulated response for Gemini OCR: %s", response)
    #     return response
    def geminiOCRreader(image_bytes,ext):
        """ Processes the image file using the Gemini OCR model.
        Args:
            imageFile (str): The path to the image file to be processed.
        Returns:
            response: The response from the Gemini OCR model containing extracted data.
        """
        prompetString = os.getenv('GEMINI_OCR_PROMPT')
        logger.debug("Starting Gem OCR Processing With prompt: %s", prompetString)
        # file = GeminiOCRreader.client.files.upload(file=imageFile)
        # Read the image file and convert it to bytes
        # image_bytes = imageFile.read()
        image = types.Part.from_bytes(
        data=image_bytes, mime_type="image/"+ext.lstrip('.') if ext else "image/jpg"  # Default to jpg if no extension is provided
        )
        client = GeminiOCRreader.client
        response = client.models.generate_content(
            model=GeminiOCRreader.model,
            contents=[prompetString,
                       image],
        )
        logger.debug("Gem completed, Response: %s for image file: %s", response.text)
        return  response.text