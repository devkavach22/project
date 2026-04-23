from fastapi import APIRouter, File, UploadFile, HTTPException
import io
from pypdf import PdfReader
from chain.CV_data_chain_new import get_cv_data_from_openrouter_model
from schemas.cv_data_schema import CVSchema

router = APIRouter()

@router.post("/cv-parser")
async def cv_parser(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        # Determine file type and extract text
        filename = file.filename.lower()
        if filename.endswith(".pdf"):
            cv_text = extract_text_from_pdf(content)
            cv_text = cv_text + extract_from_pdf_with_ocr(content)
            
        elif filename.endswith(".txt"):
            cv_text = content.decode("utf-8")

        else:
            # Fallback to direct decoding or error
            try:
                cv_text = content.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a PDF or TXT file.")

        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the file.")

        # Process the extracted text
        cv_data_extracted = get_cv_data_from_openrouter_model(cv_text)
        
        return {
            "message": "File processed successfully",
            "data": cv_data_extracted
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        if "402" in error_msg or "credits" in error_msg.lower() or "max_tokens" in error_msg.lower():
            raise HTTPException(
                status_code=402, 
                detail=f"OpenRouter Credit/Limit Error: {error_msg}. Consider reducing max_tokens or upgrading your plan."
            )
        raise HTTPException(status_code=500, detail=f"Error processing file: {error_msg}")







def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from PDF bytes using pypdf.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def extract_from_pdf_with_ocr(pdf_bytes: bytes) -> str:
    """
    Extracts text from PDF bytes using pypdf and OCR (Tesseract).
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""