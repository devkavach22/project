from pypdf import PdfReader
from io import BytesIO
import base64
from fastapi import APIRouter, UploadFile, File
from chain.pdf_parser_chain import get_spacefix_data
from schemas.SpaceFix_Schema import SpaceFixSchema
import time

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
@router.post("/upload")
async def upload(file: UploadFile = File(..., description="The PDF file to extract data from")):
    start_total = time.time()

    # 1. Basic validation
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    # Read uploaded file
    file_bytes = await file.read()
    
    if len(file_bytes) == 0:
        return {"error": "Uploaded file is empty"}

    # -----------------------------
    # 📄 PDF Extraction टाइम
    # -----------------------------
    start_pdf = time.time()
    extracted_pdf_data = extract_pdf_content(file_bytes)
    pdf_time = time.time() - start_pdf

    # -----------------------------
    # 🤖 LLM Processing टाइम
    # -----------------------------
    start_llm = time.time()
    extracted_spacefix_data = get_spacefix_data(extracted_pdf_data["text"])
    llm_time = time.time() - start_llm

    # -----------------------------
    # ⏱️ Total टाइम
    # -----------------------------
    total_time = time.time() - start_total

    # Log in minutes and seconds
    print(f"""
    📄 PDF Time: {pdf_time / 60:.2f} min {pdf_time % 60:.2f} sec
    🤖 LLM Time: {llm_time / 60:.2f} min {llm_time % 60:.2f} sec
    ⏱️ Total Time: {total_time / 60:.2f} min {total_time % 60:.2f} sec
    """)

    return {
        "status": "success",
        "filename": file.filename,
        "extracted_text": extracted_spacefix_data,
        "images_count": len(extracted_pdf_data["images"]),
        "images_preview": extracted_pdf_data["images"] if extracted_pdf_data["images"] else [],
        
        # ✅ Timing response
        "timing": {
            "pdf_extraction_time_sec": round(pdf_time, 2),
            "llm_processing_time_sec": round(llm_time, 2),
            "total_time_sec": round(total_time, 2)
        }
    }

