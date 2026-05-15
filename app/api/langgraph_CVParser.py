from fastapi import APIRouter, File, UploadFile, HTTPException
import io
from pypdf import PdfReader
from schemas.cv_data_schema import CVSchema
import os
import easyocr
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
import asyncio
# from langgraph_agentic_CV_parser import extract_resume_agentic
from langgraph_agentic_CV_parser_without_mergeLLM import extract_resume_agentic

# from data_pipeline.file_data_extraction import FileDataExtractor
from data_pipeline.pdf_data import PDFTextExtractor

router = APIRouter()


import time
from fastapi import UploadFile, File, HTTPException

# Initialize extractor
# extractor = FileDataExtractor()

# Initialize PDF text extractor
pdf_extractor = PDFTextExtractor()

@router.post("/cv-parser-ollama")
async def cv_parser(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            # ⏱ Start timing
            start_time = time.time()

            cv_text = await pdf_extractor.extract_pdf_text(content)
            mid_time = time.time()


            # cv_text_1 = extract_text_from_pdf(content)
            # mid_time = time.time()


            # cv_text_2 = await extractor.extract_data(
            #     file_bytes=content,
            #     ext=".pdf"
            # )

            # print("cv_text_2 pdf all data:",cv_text_2,type(cv_text_2))

            end_time = time.time()
      
            # cv_text = cv_text_1 + cv_text_2
            # cv_text = cv_text_1

            # 🖨️ Print timings
            print(f"[PDF TEXT EXTRACTION] Normal PDF time: {mid_time - start_time:.2f} sec")
            print(f"[PDF TEXT EXTRACTION] OCR time: {end_time - mid_time:.2f} sec")
            print(f"[PDF TEXT EXTRACTION] Total extraction time: {end_time - start_time:.2f} sec")
 

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
        cv_data_extracted = await extract_resume_agentic(cv_text)
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


def extract_from_pdf_images_with_easyocr(pdf_bytes: bytes) -> str:
    """
    Extract text only from images embedded inside PDF using EasyOCR.

    Steps:
    1. Open PDF using PyMuPDF
    2. Extract embedded images from each page
    3. Apply EasyOCR on extracted images
    4. Return extracted text
    """

    try:
        # Initialize EasyOCR
        reader = easyocr.Reader(['en'])

        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        extracted_text = ""

        # Iterate pages
        for page_index in range(len(pdf_document)):
            page = pdf_document[page_index]

            # Get all images from page
            image_list = page.get_images(full=True)

            extracted_text += f"\n--- Page {page_index + 1} ---\n"

            # Iterate images
            for img_index, img in enumerate(image_list, start=1):

                xref = img[0]

                # Extract image bytes
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                # Open image with PIL
                pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

                # Convert to numpy array
                image_np = np.array(pil_image)

                # OCR using EasyOCR
                results = reader.readtext(image_np, detail=0)

                image_text = "\n".join(results)

                extracted_text += (
                    f"\n[Image {img_index} Text]\n{image_text}\n"
                )

        pdf_document.close()

        return extracted_text.strip()

    except Exception as e:
        print(f"Error extracting image text from PDF: {e}")
        return ""


