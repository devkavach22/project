# pdf_data.py

from pathlib import Path
from typing import Union, Optional

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


def extract_text_from_pdf(path: Union[str, Path]) -> str:
    """Extract text from a PDF file."""
    if PdfReader is None:
        raise RuntimeError(
            "pypdf not installed; install it with: pip install pypdf"
        )

    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text.strip())
    return "\n".join(text_parts)


def extract_text_from_txt(path: Union[str, Path]) -> str:
    """Extract text from a plain text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_text(path: Union[str, Path]) -> str:
    """
    Generic data‑extraction pipeline that reads text from:
      - PDF files (.pdf)
      - Plain text files (.txt)

    Returns:
      A single string containing all extracted text.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    elif suffix in (".txt", ".text"):
        return extract_text_from_txt(path)
    else:
        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            "Supported types: .pdf, .txt"
        )


# Example usage (you can remove this if you only want the module)
if __name__ == "__main__":
    # Example: pass any file path here
    file_path = "example.pdf"  # or "example.txt"
    try:
        text = extract_text(file_path)
        print("Extracted text:")
        print(text)
    except Exception as e:
        print(f"Error: {e}")