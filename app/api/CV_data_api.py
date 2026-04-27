from fastapi import APIRouter, File, UploadFile, HTTPException
import io
from pypdf import PdfReader
# from chain.CV_data_chain_new import get_cv_data_from_openrouter_model
from chain.CV_data_chain_time import get_cv_data_from_openrouter_model
# from chain.CV_data_chain_ollama_cloude import get_cv_data_from_openrouter_model
from schemas.cv_data_schema import CVSchema

router = APIRouter()

# @router.post("/cv-parser")
# async def cv_parser(file: UploadFile = File(...)):
#     try:
#         content = await file.read()
        
#         # Determine file type and extract text
#         filename = file.filename.lower()
#         if filename.endswith(".pdf"):
#             import time
#             start_time = time.time()
#             cv_text = extract_text_from_pdf(content)
#             cv_text = cv_text + extract_from_pdf_with_ocr(content)
#             end_time = time.time()
#             print(f"⏱️ PDF data extraction took {end_time - start_time:.2f} seconds")
            
#         elif filename.endswith(".txt"):
#             cv_text = content.decode("utf-8")

#         else:
#             # Fallback to direct decoding or error
#             try:
#                 cv_text = content.decode("utf-8")
#             except UnicodeDecodeError:
#                 raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a PDF or TXT file.")

#         if not cv_text.strip():
#             raise HTTPException(status_code=400, detail="Could not extract text from the file.")

#         # Process the extracted text
#         cv_data_extracted = get_cv_data_from_openrouter_model(cv_text)
        
#         return {
#             "message": "File processed successfully",
#             "data": cv_data_extracted
#         }
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         error_msg = str(e)
#         if "402" in error_msg or "credits" in error_msg.lower() or "max_tokens" in error_msg.lower():
#             raise HTTPException(
#                 status_code=402, 
#                 detail=f"OpenRouter Credit/Limit Error: {error_msg}. Consider reducing max_tokens or upgrading your plan."
#             )
#         raise HTTPException(status_code=500, detail=f"Error processing file: {error_msg}")



import time
from fastapi import UploadFile, File, HTTPException

@router.post("/cv-parser")
async def cv_parser(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            # ⏱ Start timing
            start_time = time.time()

            cv_text_1 = extract_text_from_pdf(content)
            mid_time = time.time()

            cv_text_2 = extract_from_pdf_with_ocr(content)
            end_time = time.time()

            cv_text = cv_text_1 + cv_text_2

            # 🖨️ Print timings
            print(f"[PDF TEXT EXTRACTION] Normal PDF time: {mid_time - start_time:.2f} sec")
            print(f"[PDF TEXT EXTRACTION] OCR time: {end_time - mid_time:.2f} sec")
            print(f"[PDF TEXT EXTRACTION] Total extraction time: {end_time - start_time:.2f} sec")

        elif filename.endswith(".txt"):
            start_time = time.time()

            cv_text = content.decode("utf-8")

            end_time = time.time()
            print(f"[TXT EXTRACTION] Time: {end_time - start_time:.2f} sec")

        else:
            try:
                start_time = time.time()

                cv_text = content.decode("utf-8")

                end_time = time.time()
                print(f"[FALLBACK EXTRACTION] Time: {end_time - start_time:.2f} sec")

            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file format. Please upload a PDF or TXT file."
                )

        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the file.")

        # ⏱ LLM processing time
        llm_start = time.time()
        cv_data_extracted = get_cv_data_from_openrouter_model(cv_text)
        llm_end = time.time()

        print(f"[LLM PROCESSING] Time: {llm_end - llm_start:.2f} sec")

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