"""
PDF Reader Module
Converts PDF plan sheets to high-resolution images for processing
"""

from pdf2image import convert_from_path
import uuid
import os
import platform
from typing import List


def pdf_to_images(pdf_path: str, dpi: int = 200) -> List[str]:
    """
    Convert a PDF file to a list of image paths

    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for image conversion (default 300 for engineering plans)

    Returns:
        List of file paths to generated PNG images
    """

    print(f"Converting PDF: {pdf_path}")
    print(f"Resolution: {dpi} DPI")

    try:
        # Convert PDF pages to images
        # On Windows, pdf2image often needs the explicit Poppler path
        system = platform.system().lower()
        if system == "windows":
            poppler_path = r"C:\\poppler\\poppler-25.12.0\\Library\\bin"
            pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
        else:
            pages = convert_from_path(pdf_path, dpi=dpi)
        print(f"Successfully converted {len(pages)} pages")

        image_paths = []

        # Save each page as a PNG
        for i, page in enumerate(pages):
            filename = f"temp_uploads/sheet_{uuid.uuid4()}_{i}.png"
            page.save(filename, "PNG")
            image_paths.append(filename)
            print(f"  Saved sheet {i+1}: {filename}")

        return image_paths

    except Exception as e:
        print(f"Error converting PDF: {str(e)}")
        raise Exception(f"Failed to convert PDF to images: {str(e)}")
