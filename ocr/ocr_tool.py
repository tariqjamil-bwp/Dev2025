# ocr_tool.py

import base64
from mistralai import Mistral

def ocr_from_file(file):
    """
    Perform OCR on a file-like object (e.g., UploadedFile from Streamlit).

    Args:
        file (file-like object): File-like object containing the document.

    Returns:
        str: Extracted text in markdown format.
    """
    # Read the file content
    file_content = file.read()

    # Initialize the Mistral client
    api_key = os.getenv("MISTRAL_API_KEY")
    client = Mistral(api_key=api_key)

    # Process the document
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_bytes",
            "document_bytes": file_content
        },
        include_image_base64=False
    )

    # Extract text from the OCR response
    extracted_text = ""
    for page in ocr_response.get("pages", []):
        extracted_text += page.get("markdown", "") + "\n"

    return extracted_text
