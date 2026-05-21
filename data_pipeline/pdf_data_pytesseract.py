
# import io
# from typing import List

# import fitz  # PyMuPDF
# from PIL import Image
# import pytesseract


# class PDFTextExtractor:

#     async def extract_pdf_text(self, file_bytes: bytes) -> str:
#         """
#         Extract text from PDF.
#         Supports:
#         1. Selectable text PDFs
#         2. OCR for scanned PDFs
#         """

#         try:

#             text = ""

#             # =====================================
#             # Extract normal selectable PDF text
#             # =====================================
#             with fitz.open(
#                 stream=io.BytesIO(file_bytes),
#                 filetype="pdf"
#             ) as pdf:

#                 for page in pdf:
#                     text += page.get_text("text")

#             result_text = text.replace("\n", " ").strip()

#             # =====================================
#             # Skip OCR if text already exists
#             # =====================================
#             if len(result_text) > 100:
#                 return result_text

#             # =====================================
#             # OCR fallback
#             # =====================================
#             ocr_text = self._ocr_pdf_pages(file_bytes)

#             return f"{result_text} {ocr_text}".strip()

#         except Exception as e:
#             return f"PDF extraction failed: {str(e)}"

#     # =====================================================
#     # OCR PDF pages
#     # =====================================================
#     def _ocr_pdf_pages(self, pdf_bytes: bytes) -> str:

#         all_text = []

#         pdf_document = fitz.open(
#             stream=io.BytesIO(pdf_bytes),
#             filetype="pdf"
#         )

#         for page_num in range(len(pdf_document)):

#             page = pdf_document.load_page(page_num)

#             # =====================================
#             # Convert page to image
#             # =====================================
#             pix = page.get_pixmap(dpi=200)

#             img = Image.open(
#                 io.BytesIO(
#                     pix.tobytes("png")
#                 )
#             )

#             # Optional optimization
#             img = img.convert("L")

#             # =====================================
#             # OCR
#             # =====================================
#             text = pytesseract.image_to_string(
#                 img,
#                 lang="eng",
#                 config="--oem 3 --psm 6"
#             )

#             all_text.append(text)

#         pdf_document.close()

#         return " ".join(all_text)



#######################################################

import io
import time

import fitz  # PyMuPDF
from PIL import Image
import pytesseract


class PDFTextExtractor:

    async def extract_pdf_text(self, file_bytes: bytes) -> dict:
        """
        Extract text from PDF.

        Returns:
        {
            "text": str,
            "normal_pdf_time": float,
            "ocr_time": float,
            "total_time": float,
            "ocr_used": bool
        }
        """

        total_start = time.time()

        try:

            text = ""

            # =====================================================
            # NORMAL PDF EXTRACTION TIMER
            # =====================================================
            normal_start = time.time()

            with fitz.open(
                stream=io.BytesIO(file_bytes),
                filetype="pdf"
            ) as pdf:

                for page in pdf:
                    text += page.get_text("text")

            result_text = text.replace("\n", " ").strip()

            normal_end = time.time()

            normal_pdf_time = normal_end - normal_start

            # =====================================================
            # SKIP OCR IF TEXT EXISTS
            # =====================================================
            if len(result_text) > 100:

                total_end = time.time()

                return {
                    "text": result_text,
                    "normal_pdf_time": round(normal_pdf_time, 2),
                    "ocr_time": 0,
                    "total_time": round(total_end - total_start, 2),
                    "ocr_used": False
                }

            # =====================================================
            # OCR TIMER
            # =====================================================
            ocr_start = time.time()

            ocr_text = self._ocr_pdf_pages(file_bytes)

            ocr_end = time.time()

            total_end = time.time()

            return {
                "text": f"{result_text} {ocr_text}".strip(),
                "normal_pdf_time": round(normal_pdf_time, 2),
                "ocr_time": round(ocr_end - ocr_start, 2),
                "total_time": round(total_end - total_start, 2),
                "ocr_used": True
            }

        except Exception as e:

            total_end = time.time()

            return {
                "text": f"PDF extraction failed: {str(e)}",
                "normal_pdf_time": 0,
                "ocr_time": 0,
                "total_time": round(total_end - total_start, 2),
                "ocr_used": False
            }

    # =====================================================
    # OCR PDF PAGES
    # =====================================================
    def _ocr_pdf_pages(self, pdf_bytes: bytes) -> str:

        all_text = []

        pdf_document = fitz.open(
            stream=io.BytesIO(pdf_bytes),
            filetype="pdf"
        )

        for page_num in range(len(pdf_document)):

            page = pdf_document.load_page(page_num)

            # =====================================================
            # Convert PDF page -> Image
            # =====================================================
            pix = page.get_pixmap(dpi=200)

            img = Image.open(
                io.BytesIO(
                    pix.tobytes("png")
                )
            )

            # =====================================================
            # Optional preprocessing
            # =====================================================
            img = img.convert("L")

            # =====================================================
            # OCR
            # =====================================================
            text = pytesseract.image_to_string(
                img,
                lang="eng",
                config="--oem 3 --psm 6"
            )

            all_text.append(text)

        pdf_document.close()

        return " ".join(all_text)