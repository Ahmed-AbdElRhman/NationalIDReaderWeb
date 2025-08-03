from flask import jsonify
import os

from app.Services import GeminiOCRreader

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
    def api_process(Imagefile):

        ocrHandler = GeminiOCRreader.GeminiOCRreader(
            api_key=os.getenv('GOOGLE_API_KEY'),
            model=os.getenv('GOOGLE_OCR_MODEL', 'gemini-2.0-flash-001')
        )
        if not Imagefile:
                raise ValueError("No image file provided")
        try:
            data = ocrHandler.geminiOCRreader(Imagefile)
        except Exception as e:
            raise Exception(f"Error processing image OCR: {str(e)}")

        result = {
            'first_name': data.get('firstname', "N/A"),
            'second_name': data.get('parname', "N/A"),
            'full_name': f"{data.get('firstname', 'N/A')} {data.get('parname', 'N/A')}",
            'national_id': data.get('nationalID', "N/A"),
            'address': data.get('address', "N/A"),
            'birth': data.get('birthdate', "N/A"),
            'gov': data.get('gov', "N/A"),
            'gender': data.get('gender', "N/A"),
        }
        return jsonify(result)




