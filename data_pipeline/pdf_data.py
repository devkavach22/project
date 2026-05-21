import io
from typing import List
import fitz  # PyMuPDF
import easyocr
import pytesseract
from PIL import Image


class PDFTextExtractor:

    def __init__(self):
        """Initialize PDFTextExtractor, ensuring required OCR dependencies."""
        self._ensure_pytesseract()
        # Lazy loading for OCR model (EasyOCR) loads only when needed
        self.reader = None

    # =========================================================
    # LOAD OCR MODEL ONLY WHEN REQUIRED
    # =========================================================
    def _ensure_pytesseract(self):
        """Check if pytesseract is available; install it via uv if missing."""
        try:
            import importlib
            importlib.import_module("pytesseract")
        except ImportError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "uv", "pip", "install", "pytesseract"], check=True)
        # Verify import after installation
        import pytesseract  # noqa: F401

    def get_reader(self):
        if self.reader is None:
            print("[OCR] Loading EasyOCR model...")
            self.reader = easyocr.Reader(
                ["en"],
                gpu=False,
                download_enabled=False
            )
        return self.reader

    async def extract_pdf_text(self, file_bytes: bytes) -> str:
        """
        Extract text from PDF.
        Supports:
        1. Normal selectable PDF text
        2. OCR from images inside PDF
        """

        try:
            # =========================
            # Extract normal PDF text
            # =========================
            text = ""

            with fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf") as pdf:

                for page in pdf:
                    text += page.get_text("text")

            result_text = text.replace("\n", " ").strip()

            # 🚀 OPTIMIZATION: Skip OCR if PDF already contains selectable text
            # Resumes usually have > 100 chars if they are not scanned images.
            if len(result_text) > 100:
                return result_text

            # =========================
            # Extract images from PDF
            # =========================
            images = self._extract_images_from_pdf(file_bytes)

            # =========================
            # OCR on extracted images
            # =========================
            if images:
                image_text = self._extract_text_from_images(images)
                result_text += " " + image_text

            return result_text.strip()

        except Exception as e:
            return f"PDF extraction failed: {str(e)}"

    # =====================================================
    # Extract images from PDF
    # =====================================================
    def _extract_images_from_pdf(self, pdf_bytes: bytes) -> List[bytes]:

        images = []

        pdf_document = fitz.open(
            stream=io.BytesIO(pdf_bytes),
            filetype="pdf"
        )

        for page_num in range(len(pdf_document)):

            page = pdf_document.load_page(page_num)

            for img in page.get_images(full=True):

                xref = img[0]

                base_image = pdf_document.extract_image(xref)

                image_bytes = base_image["image"]

                images.append(image_bytes)

        pdf_document.close()

        return images

    # =====================================================
    # OCR from images
    # =====================================================
    


        all_text = []
        reader = self.get_reader()

        for img_bytes in image_bytes_list:

            result = reader.readtext(
                img_bytes,
                detail=0,
                paragraph=True
            )

            all_text.append(" ".join(result))

        return " ".join(all_text)