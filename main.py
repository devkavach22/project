from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
from io import BytesIO
from chain.pdf_parser_chain import get_spacefix_data
import base64
import sys,os
from fastapi.middleware.cors import CORSMiddleware
from schemas.SpaceFix_Schema import SpaceFixSchema

# Add the project root to sys.path so that 'schemas' can be found when this file is run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
    "*"
    # Add other allowed origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allows cookies, authorization headers, etc.
    allow_methods=["*"],     # Allows all standard methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allows all headers
)

# -----------------------------
# PDF Extract Function
# -----------------------------
def extract_pdf_content(file_bytes: bytes) -> dict:
    """
    Extracts both text and images from a PDF file.
    
    Args:
        file_bytes (bytes): The raw bytes of the PDF file.
        
    Returns:
        dict: A dictionary containing:
            - "text": A concatenated string of all text found.
            - "images": A list of base64 encoded strings of the images.
    """
    pdf = PdfReader(BytesIO(file_bytes))
    
    extracted_text = ""
    images_base64 = []

    for page in pdf.pages:
        # 1. Extract Text
        page_text = page.extract_text()
        if page_text:
            extracted_text += " " + page_text

        # 2. Extract Images
        # pypdf stores images in the page.images object
        if hasattr(page, "images"):
            for image_file in page.images:
                try:
                    # Get the raw image bytes
                    image_data = image_file.data
                    # Encode to base64 string
                    base64_str = base64.b64encode(image_data).decode('utf-8')
                    images_base64.append(base64_str)
                except Exception:
                    # Skip images that fail to process
                    continue

    return {
        "text": extracted_text.strip(),
        "images": images_base64
    }


# -----------------------------
# Upload Route
# -----------------------------
@app.post("/upload",response_model=SpaceFixSchema)
async def upload(file: UploadFile = File(..., description="The PDF file to extract data from")):
    # 1. Basic validation
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    # Read uploaded file
    file_bytes = await file.read()
    
    if len(file_bytes) == 0:
        return {"error": "Uploaded file is empty"}

    # Extract data from PDF
    extracted_pdf_data = extract_pdf_content(file_bytes)
    
    # Extract data from PDF (Chain)
    extracted_spacefix_data = get_spacefix_data(extracted_pdf_data["text"])

    # Log/Print extraction summary
    print(f"Processed file: {file.filename}, Text length: {len(extracted_pdf_data['text'])}")

    return {
        "status": "success",
        "filename": file.filename,
        "extracted_text": extracted_spacefix_data,
        "images_count": len(extracted_pdf_data["images"]),
        "images_preview": extracted_pdf_data["images"] if extracted_pdf_data["images"] else []
    }


# from pydantic import BaseModel

# class Item(BaseModel):
#     name: str
#     description: str


@app.get("/")
async def root():
    return {"message": "Hello World"}