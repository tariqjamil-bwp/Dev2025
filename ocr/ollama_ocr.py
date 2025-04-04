from ollama_ocr import OCRProcessor

# Create an instance with the new model
ocr = OCRProcessor(model_name='granite3.2-vision')

# Process a PDF file
result = ocr.process_image(
    image_path="input/pdf.pdf",  # Replace with your PDF file path
    format_type="text",           # Options: markdown, text, json, structured, key_value, table
    language="eng"                # Specify language if supported by the model
    #custom_prompt= ""            # overwrite the default format type
)

print(result)
