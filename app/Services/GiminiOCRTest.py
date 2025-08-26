import google.generativeai as genai
import base64
import json
import os

# Your API key will be provided by the environment, but you can also set it here
# if needed for local testing.
genai.configure(api_key="AIzaSyAik3z3ti8T1naBujWuN24MDZfTomMwzhQ")

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
        "lastname": {
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

# Define the model and generation configuration
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-05-20",
    generation_config={"response_mime_type": "application/json", "response_schema": response_schema}
)

# The prompt with instructions for the model
prompt_text = """
    From the Egyptian National ID card image, extract the following information.
    For each field, provide both the Arabic and English text.
    - First Name: The first name in both Arabic and English.
    - Last Name: The full last name in both Arabic and English.
    - National ID: The 14-digit number at the bottom center. Provide this in both Arabic numerals (as seen on the card) and Western numerals.
    - Address: The full address in both Arabic and English.
    
    The extracted information should be returned as a single JSON object with the following nested keys: "firstname", "lastname", "NationalID", and "address". Each of these should contain a nested object with "arabic" and "english" string fields.
"""


def process_id_card_with_genai(image_path: str):
    """
    Processes an Egyptian National ID card image to extract key information
    in both Arabic and English using the google-generativeai library.

    Args:
        image_path (str): The file path to the image to be processed.
    
    Returns:
        dict: A dictionary containing the extracted information in both languages,
              or None if an error occurs.
    """
    try:
        # Load the image data
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        # Determine the MIME type
        # For simplicity, we assume jpeg based on the prompt, but you could
        # use a library like `filetype` to detect it dynamically.
        mime_type = "image/jpeg"

        # The correct way to define the schema is now using a dictionary
 
        # Prepare the parts of the prompt, including the image
        prompt_parts = [
            prompt_text,
            {"mime_type": mime_type, "data": image_data}
        ]

        # Generate content with the model
        response = model.generate_content(prompt_parts)

        # The response is a ContentResponse object. The JSON is in the text attribute.
        if response.text:
            return json.loads(response.text)
        else:
            print("Error: The API response did not contain the expected data.")
            return None

    except FileNotFoundError:
        print(f"Error: The file at {image_path} was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# --- Example usage ---
if __name__ == "__main__":
    # Replace 'path/to/your/image.jpg' with the actual path to your uploaded image
    # For this example, we assume 'Sample.jpg' is in the same directory as the script.
    image_file = "C:/Users/Administrator/Downloads/Sample/Sample.jpg"
    
    extracted_info = process_id_card_with_genai(image_file)
    
    if extracted_info:
        print("\nExtracted Information:")
        print(extracted_info)
        extracted_infojs= json.dumps(extracted_info, indent=4, ensure_ascii=False)
        
        print(extracted_infojs)
        print("Hii")
        print(extracted_info["NationalID"]["arabic"])
    else:
        print("\nCould not extract information from the image.")
