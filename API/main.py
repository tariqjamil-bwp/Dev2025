import logging
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add this before creating the FastAPI app instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert-pdf/")
async def convert_pdf_to_markdown(file: UploadFile = File(...)):
    try:
        logger.info("Received request to convert PDF to Markdown.")

        # Read the PDF file
        pdf_document = fitz.open(stream=file.file.read(), filetype="pdf")
        markdown_text = ""

        # Extract text from each page
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text")
            markdown_text += text + "\n\n"

        logger.info("Successfully converted PDF to Markdown.")
        return JSONResponse(content={"markdown": markdown_text})
    except Exception as e:
        logger.error(f"Error converting PDF to Markdown: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
