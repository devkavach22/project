from pypdf import PdfReader
from io import BytesIO
import base64
from fastapi import APIRouter, UploadFile, File
from chain.pdf_parser_chain import get_spacefix_data
from schemas.SpaceFix_Schema import SpaceFixSchema

router = APIRouter()


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
@router.post("/upload",response_model=SpaceFixSchema)
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

