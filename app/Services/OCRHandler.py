from google import genai
from app.utils.logger import get_logger
logger = get_logger(__name__)
def geminiOCRreader(key,imagePath):
    print("OCR Model Started")
    client = genai.Client(api_key=key)
    file = client.files.upload(file=imagePath)
    response = client.models.generate_content(
     model="gemini-2.0-flash-001",
        # contents=['This is an Arabic National ID card, which contains the his name,parent full name,adress, national ID (Arabic numbers), and other data. Act as a highly accurate and specialized Arabic Optical Character Recognition (OCR) system, so please extract all Arabic characters/numbers from the image, be proficient in interpreting Arabic National ID cards, and send the response as a fixed JSON form containing {firstname:{arabic:"",english:""},parname:{arabic:"",english:""},address:{arabic:"",english:""},nationalID:{arabic:"",english:""} }. You can also predict the word that was not read correctly.'
        contents=['This is an Arabic National ID card, which contains the his name,parent full name,adress, national ID (Arabic numbers), and other data. Act as a highly accurate and specialized Arabic Optical Character Recognition (OCR) system, so please extract all Arabic characters/numbers from the image, be proficient in interpreting Arabic National ID cards, and send the response as a fixed JSON form containing {firstname:"",parname:"",address:"",nationalID:"}. You can also predict the word that was not read correctly.make it fast an acurate and make sure to return all data in english'
                  , file]
    )
    return response
class GeminiOCRreader:
    _instance = None
    client = None
    model = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GeminiOCRreader, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self, api_key=None,model="gemini-2.0-flash-001"):

        """ Initializes the GeminiOCRreader with an API key and model.
        Args:
            api_key (str): The API key for the Gemini service.
            model (str): The model to be used for OCR processing.
        """
        # This ensures that the service is a singleton and only initialized once
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.client = genai.Client(api_key=api_key)
            self.model = model
            logger.debug("GeminiOCRreader initialized with API key.")
    # This method processes the image file using the Gemini OCR model.
    def geminiOCRreader(self, imageFile):
        """ Processes the image file using the Gemini OCR model.
        Args:
            imageFile (str): The path to the image file to be processed.
        Returns:
            response: The response from the Gemini OCR model containing extracted data.
        """
        print("OCR Model Started")
        file = self.client.files.upload(file=imageFile)
        response = self.client.models.generate_content(
        model=self.model,
            contents=['This is an Arabic National ID card, which contains the his name,parent full name,adress, national ID (Arabic numbers), and other data. Act as a highly accurate and specialized Arabic Optical Character Recognition (OCR) system, so please extract all Arabic characters/numbers from the image, be proficient in interpreting Arabic National ID cards, and send the response as a fixed JSON form containing {firstname:"",parname:"",address:"",nationalID:"}. You can also predict the word that was not read correctly.make it fast an acurate and make sure to return all data in english'
                    , file]
        )
        return response