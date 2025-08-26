import google.generativeai as genai
# from google.genai import types
import json

from app.utils.logger import get_logger
logger = get_logger(__name__)

from dotenv import load_dotenv
import os
load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
class GeminiOCRreader:
    # client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
    # model = os.getenv('GOOGLE_OCR_MODEL', 'gemini-2.0-flash-001')
    # This method processes the image file using the Gemini OCR model.
    response_schema = {
    "type": "OBJECT",
    "properties": {
        "firstname": {
            "type": "OBJECT",
            "properties": {
                "arabic": {"type": "STRING"},
                "english": {"type": "STRING"}
            }
        },
        "parentfullname": {
            "type": "OBJECT",
            "properties": {
                "arabic": {"type": "STRING"},
                "english": {"type": "STRING"}
            }
        },
        "NationalID": {
            "type": "OBJECT",
            "properties": {
                "arabic": {"type": "STRING"},
                "english": {"type": "STRING"}
            }
        },
        "address": {
            "type": "OBJECT",
            "properties": {
                "arabic": {"type": "STRING"},
                "english": {"type": "STRING"}
            }
        }
    }
}
    # Define the model and generation configuration "gemini-2.5-flash-preview-05-20"
    model = genai.GenerativeModel(
        model_name=os.getenv('GOOGLE_OCR_MODEL', 'gemini-2.0-flash-001'),
        generation_config={"response_mime_type": "application/json", "response_schema": response_schema}
    )
    # The prompt with instructions for the model
    # prompetString = os.getenv('GEMINI_OCR_PROMPT')
    prompt_text = """
        From the Egyptian National ID card image, extract the following information.
        For each field, provide both the Arabic and English text.
        - First Name: The first name in both Arabic and English.
        - Parent Full Name: The full last name in both Arabic and English.
        - National ID: The 14-digit number at the bottom center. Provide this in both Arabic numerals (as seen on the card) and Western numerals.
        - Address: The full address in both Arabic and English.
        
        The extracted information should be returned as a single JSON object with the following nested keys: "firstname", "parentfullname", "NationalID", and "address". Each of these should contain a nested object with "arabic" and "english" string fields.
    """
    @staticmethod
    def geminiOCRreader(image_bytes,ext):
        """ Processes the image file using the Gemini OCR model.
        Args:
            imageFile (str): The path to the image file to be processed.
        Returns:
            response: The response from the Gemini OCR model containing extracted data.
        """
        mime_type = "image/"+ext.lstrip('.') if ext else "image/jpg"
        logger.debug("Starting Gem OCR Processing With prompt: %s",GeminiOCRreader.prompt_text)
        # file = GeminiOCRreader.client.files.upload(file=imageFile)
        # Read the image file and convert it to bytes
        # image_bytes = imageFile.read()
        # image = types.Part.from_bytes(
        # data=image_bytes, mime_type=mime_type  # Default to jpg if no extension is provided
        # )

        # Prepare the parts of the prompt, including the image
        prompt_parts = [
            GeminiOCRreader.prompt_text,
            {"mime_type": mime_type, "data": image_bytes}
        ]

        # Generate content with the model
        response = GeminiOCRreader.model.generate_content(prompt_parts)
        responseJeson = json.loads(response.text)
        # The response is a ContentResponse object. The JSON is in the text attribute.
        if response.text:
            logger.debug("Gem completed, Response IS:")
            logger.debug(responseJeson)
            return responseJeson
        else:
            print("Error: The API response did not contain the expected data.")
            logger.error("Gemini OCR response is empty or does not contain text.")
            raise ValueError("Gemini OCR response is empty or does not contain text.")

