"""
Egyptian National ID OCR Reader using Google Gemini 2.0 Flash
Professional implementation with prompt caching and structured output
"""

import os
import json
import base64
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field
import google.generativeai as genai
from google.generativeai.caching import CachedContent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BilingualField(BaseModel):
    """Model for bilingual field with Arabic and English versions"""
    arabic: str = Field(description="Text in Arabic")
    english: str = Field(description="Text in English (transliterated or translated)")

class NatIDInfo(BaseModel):
    """Structured model for Egyptian National ID information with bilingual support"""
    firstname: BilingualField = Field(description="First name in Arabic and English")
    lastname: BilingualField = Field(description="Full last name in Arabic and English")
    NationalID: BilingualField = Field(description="14-digit National ID number in Arabic and Western numerals")
    address: BilingualField = Field(description="Full address in Arabic and English")

class EgyptianIDReader:
    """Professional Egyptian National ID OCR reader with caching support"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-001"):
        """
        Initialize the ID reader with API credentials
        
        Args:
            api_key: Google AI API key
            model_name: Gemini model name to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.cached_content = None
        self.model = None
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self._initialize_model()
        
        # Create cached content for the prompt
        self._setup_prompt_cache()
    
    def _initialize_model(self):
        """Initialize the Gemini model with optimal configuration"""
        generation_config = {
            "temperature": 0.1,  # Low temperature for consistent OCR results
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
            "response_mime_type": "application/json",
            "response_schema": NatIDInfo
        }
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
        )
    
    def _get_system_prompt(self) -> str:
        """
        Get the optimized system prompt for Egyptian National ID OCR with bilingual support
        This prompt is designed to be cached for better performance
        """
        return """You are a professional OCR specialist for Egyptian National ID cards. Your task is to extract specific information from Egyptian National ID images with high accuracy and provide both Arabic and English versions for each field.

IMPORTANT INSTRUCTIONS:
1. Extract text EXACTLY as it appears on the ID card
2. Preserve Arabic text in its original form
3. Provide accurate English transliteration/translation for each field
4. For numbers, provide both Arabic-Indic numerals and Western numerals
5. Maintain original formatting and spacing

EXTRACTION REQUIREMENTS:

1. FIRST NAME (firstname):
   - Location: Top right area of the card, first word after the header
   - Arabic: Extract the exact Arabic text as it appears
   - English: Provide accurate English transliteration
   - Example: Arabic: "أحمد", English: "Ahmed"

2. LAST NAME (lastname):
   - Location: Below the first name, contains the full remaining name
   - Arabic: Extract the complete Arabic name sequence excluding the first name
   - English: Provide accurate English transliteration of the full last name
   - Example: Arabic: "فتحى محمد احمد العدوى", English: "Fathy Mohamed Ahmed El-Adawy"

3. NATIONAL ID (NationalID):
   - Location: Large numbers displayed prominently on the card
   - Always 14 digits
   - Arabic: Numbers as they appear on the card (Arabic-Indic numerals)
   - English: Convert to Western numerals (0-9)
   - Example: Arabic: "٢٩٦٠٩١٥١٨٠٢٧٣١", English: "29609151802731"

4. ADDRESS (address):
   - Location: Lower section of the card, contains street and area information
   - Arabic: Extract the complete address line preserving original formatting
   - English: Provide accurate English translation/transliteration
   - Example: Arabic: "٤٦ش العروسي - ش بديع- طوسون روض الفرج- القاهره", English: "46 Al-Arousi St - Badeea St - Tawsoun Rod El-Farag - Cairo"

TRANSLITERATION GUIDELINES:
- Use standard Arabic-to-English transliteration rules
- For addresses: translate street names and areas when possible
- Maintain proper capitalization in English
- Use common English spellings for well-known places (Cairo for القاهرة)

QUALITY STANDARDS:
- Accuracy is critical - double-check each field
- If any field is unclear, mark Arabic as "غير واضح" and English as "Unclear"
- Ensure consistency in transliteration style
- Preserve Arabic diacritics and special characters in Arabic fields

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{
  "firstname": {"arabic": "...", "english": "..."},
  "lastname": {"arabic": "...", "english": "..."},
  "NationalID": {"arabic": "...", "english": "..."},
  "address": {"arabic": "...", "english": "..."}
}"""

    def _setup_prompt_cache(self):
        """Setup prompt caching for optimal performance"""
        try:
            system_prompt = self._get_system_prompt()
            
            # Create cached content with the system prompt
            self.cached_content = CachedContent.create(
                model=self.model_name,
                contents=[{
                    'role': 'user',
                    'parts': [{'text': system_prompt}]
                }],
                ttl="1h",  # Cache for 1 hour
                display_name="egyptian_id_ocr_prompt"
            )
            
            # Create model with cached content
            self.cached_model = genai.GenerativeModel.from_cached_content(
                cached_content=self.cached_content
            )
            
            logger.info("Prompt caching setup successful")
            
        except Exception as e:
            logger.warning(f"Prompt caching failed, using regular model: {e}")
            self.cached_model = self.model
    
    def _encode_image(self, image_path: str) -> Dict[str, Any]:
        """
        Encode image file to base64 format for API
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image data for API
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine MIME type based on file extension
            file_extension = Path(image_path).suffix.lower()
            mime_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp'
            }
            
            mime_type = mime_type_map.get(file_extension, 'image/jpeg')
            
            return {
                'mime_type': mime_type,
                'data': image_data
            }
            
        except Exception as e:
            raise ValueError(f"Error encoding image {image_path}: {str(e)}")
    
    def extract_id_info(self, image_path: str) -> Optional[NatIDInfo]:
        """
        Extract information from Egyptian National ID image
        
        Args:
            image_path: Path to the ID card image
            
        Returns:
            NatIDInfo object with extracted information or None if failed
        """
        try:
            # Encode the image
            image_data = self._encode_image(image_path)
            
            # Prepare the content for the model
            content = [
                "Analyze this Egyptian National ID card and extract the required information according to the instructions provided.",
                image_data
            ]
            
            # Generate response using cached model
            response = self.cached_model.generate_content(content)
            
            # Parse the JSON response
            result_json = json.loads(response.text)
            
            # Validate and create NatIDInfo object
            id_info = NatIDInfo(**result_json)
            
            logger.info(f"Successfully extracted ID info from {image_path}")
            return id_info
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
            return None
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return None
    
    def batch_process(self, image_paths: list) -> Dict[str, Optional[NatIDInfo]]:
        """
        Process multiple ID images in batch
        
        Args:
            image_paths: List of paths to ID card images
            
        Returns:
            Dictionary mapping image paths to extracted information
        """
        results = {}
        
        for image_path in image_paths:
            logger.info(f"Processing {image_path}")
            results[image_path] = self.extract_id_info(image_path)
        
        return results
    
    def cleanup_cache(self):
        """Clean up cached content"""
        try:
            if self.cached_content:
                self.cached_content.delete()
                logger.info("Cache cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error cleaning up cache: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_cache()

# Usage Example and Testing
def main():
    """Example usage of the EgyptianIDReader"""
    
    # Replace with your actual Google AI API key
    API_KEY = "AIzaSyAik3z3ti8T1naBujWuN24MDZfTomMwzhQ"
    
    # Initialize the ID reader
    with EgyptianIDReader(api_key=API_KEY) as id_reader:
        
        # Process a single image
        image_path = "C:/Users/Administrator/Downloads/Sample/Sample.jpg"
        
        try:
            result = id_reader.extract_id_info(image_path)
            
            if result:
                print("Extraction successful!")
                print(f"First Name - Arabic: {result.firstname.arabic}, English: {result.firstname.english}")
                print(f"Last Name - Arabic: {result.lastname.arabic}, English: {result.lastname.english}")
                print(f"National ID - Arabic: {result.NationalID.arabic}, English: {result.NationalID.english}")
                print(f"Address - Arabic: {result.address.arabic}, English: {result.address.english}")
                
                # Convert to dictionary if needed
                result_dict = result.model_dump()
                print(f"\nJSON Output: {json.dumps(result_dict, ensure_ascii=False, indent=2)}")
                
            else:
                print("Failed to extract information from the ID")
                
        except Exception as e:
            print(f"Error: {e}")

# # FastAPI Integration Example
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import JSONResponse
# import tempfile

# app = FastAPI(title="Egyptian ID OCR API")

# # Global ID reader instance
# id_reader = None

# @app.on_event("startup")
# async def startup_event():
#     global id_reader
#     api_key = os.getenv("GOOGLE_AI_API_KEY")
#     if not api_key:
#         raise ValueError("GOOGLE_AI_API_KEY environment variable not set")
    
#     id_reader = EgyptianIDReader(api_key=api_key)

# @app.on_event("shutdown")
# async def shutdown_event():
#     global id_reader
#     if id_reader:
#         id_reader.cleanup_cache()

# @app.post("/extract-id", response_model=NatIDInfo)
# async def extract_id_endpoint(file: UploadFile = File(...)):
#     """
#     API endpoint to extract information from uploaded Egyptian ID image
#     """
#     if not file.content_type.startswith('image/'):
#         raise HTTPException(status_code=400, detail="File must be an image")
    
#     try:
#         # Save uploaded file temporarily
#         with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
#             content = await file.read()
#             temp_file.write(content)
#             temp_file_path = temp_file.name
        
#         # Extract information
#         result = id_reader.extract_id_info(temp_file_path)
        
#         # Clean up temporary file
#         os.unlink(temp_file_path)
        
#         if result:
#             return result
#         else:
#             raise HTTPException(status_code=422, detail="Could not extract information from the ID")
            
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    print("Running Egyptian ID OCR Reader Example")
    main()