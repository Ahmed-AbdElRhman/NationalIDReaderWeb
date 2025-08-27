import base64
import requests
import json
import time

def process_id_card(image_path: str):
    """
    Processes an Egyptian National ID card image to extract key information
    in both Arabic and English using the Gemini API.

    Args:
        image_path (str): The file path to the image to be processed.
    
    Returns:
        dict: A dictionary containing the extracted information in both languages.
    """
    try:
        # Load the image and encode it to base64
        with open(image_path, "rb") as image_file:
            print(f"Processing image: {image_path}")
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            print(f"Processing image2: {image_path}")

        # Define the prompt for the model. This is the "cached" part of the prompt.
        prompt = """
            From the Egyptian National ID card image, extract the following information.
            For each field, provide both the Arabic and English text.
            - First Name: The first name in both Arabic and English.
            - Last Name: The full last name in both Arabic and English.
            - National ID: The 14-digit number at the bottom center. Provide this in both Arabic numerals (as seen on the card) and Western numerals.
            - Address: The full address in both Arabic and English.
            
            The extracted information should be returned as a single JSON object with the following nested keys: "firstname", "lastname", "NationalID", and "address". Each of these should contain a nested object with "arabic" and "english" string fields.
        """

        # Define the generation configuration for structured JSON output
        generation_config = {
            "responseMimeType": "application/json",
            "responseSchema": {
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
                },
                "propertyOrdering": ["firstname", "lastname", "NationalID", "address"]
            }
        }

        # The payload to send to the Gemini API
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg", # Use the correct MIME type for the image
                                "data": encoded_string
                            }
                        }
                    ],
                }
            ],
            "generationConfig": generation_config
        }

        # The API key is left as an empty string, as it will be provided by the environment
        api_key = "AIzaSyAik3z3ti8T1naBujWuN24MDZfTomMwzhQ"
        model_name = "gemini-2.5-flash-preview-05-20"
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        max_retries = 5
        initial_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Make the API call using the requests library
                response = requests.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=30  # Set a timeout for the request
                )
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                response_data = response.json()
                
                # Extract the JSON text from the response
                if (response_data and 'candidates' in response_data and
                    len(response_data['candidates']) > 0 and
                    'content' in response_data['candidates'][0] and
                    'parts' in response_data['candidates'][0]['content'] and
                    len(response_data['candidates'][0]['content']['parts']) > 0):
                    
                    json_text = response_data['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(json_text)
                
                else:
                    print("Error: The API response did not contain the expected data.")
                    return None

            except requests.exceptions.HTTPError as http_err:
                if http_err.response.status_code == 429 and attempt < max_retries - 1:
                    print(f"Rate limit exceeded (429). Retrying in {initial_delay * (2 ** attempt)} seconds...")
                    time.sleep(initial_delay * (2 ** attempt))
                else:
                    raise  # Re-raise the exception for other HTTP errors or last attempt
            except requests.exceptions.RequestException as req_err:
                print(f"An error occurred during the request: {req_err}")
                return None

        print("Failed to get a response after multiple retries.")
        return None
    except Exception as e:
        print(f"An error occurred while processing the image: {e}")
        return None
# --- Example usage ---
if __name__ == "__main__":
    # Replace 'path/to/your/image.jpg' with the actual path to your uploaded image
    # For this example, we assume 'Sample.jpg' is in the same directory as the script.
    image_file = "C:/Users/Administrator/Downloads/Sample/Sample.jpg"
    
    extracted_info = process_id_card(image_file)
    
    if extracted_info:
        print("\nExtracted Information:")
        print(json.dumps(extracted_info, indent=4, ensure_ascii=False))
    else:
        print("\nCould not extract information from the image.")
