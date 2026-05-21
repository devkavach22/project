import time
import asyncio
import os
from data_pipeline.pdf_data_pytesseract import PDFTextExtractor

async def main():
    pdf_path = r"C:\Users\deepak.p\Desktop\project\BALRAM_OCR_CV.pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return
    with open(pdf_path, "rb") as f:
        data = f.read()
    extractor = PDFTextExtractor()
    start = time.time()
    result = await extractor.extract_pdf_text(data)
    elapsed = time.time() - start
    print("--- Extraction Result ---")
    print(result)
    print(f"Extraction took {elapsed:.2f} seconds")

async def main():
    pdf_path = r"C:\Users\deepak.p\Desktop\project\BALRAM_OCR_CV.pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return
    with open(pdf_path, "rb") as f:
        data = f.read()
    extractor = PDFTextExtractor()
    start = time.time()
    result = await extractor.extract_pdf_text(data)
    elapsed = time.time() - start
    print("--- Extraction Result ---")
    print(result)
    print(f"Extraction took {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
