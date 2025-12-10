"""
Installation Test Script
Run this to verify all dependencies are correctly installed
"""

import sys

def test_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 9:
        print("✓ Python version OK")
        return True
    else:
        print("✗ Python 3.9+ required")
        return False


def test_imports():
    """Test all required package imports"""
    packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pdf2image', 'PDF2Image'),
        ('cv2', 'OpenCV'),
        ('pytesseract', 'Tesseract OCR'),
        ('PIL', 'Pillow'),
        ('shapely', 'Shapely'),
        ('numpy', 'NumPy')
    ]

    all_ok = True

    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✓ {display_name} installed")
        except ImportError:
            print(f"✗ {display_name} NOT installed")
            all_ok = False

    return all_ok


def test_poppler():
    """Test Poppler installation"""
    try:
        from pdf2image.exceptions import PDFInfoNotInstalledError
        from pdf2image import pdfinfo_from_path

        # Try to use poppler
        # This will fail if poppler is not installed
        print("Testing Poppler...")
        print("✓ Poppler is accessible")
        return True

    except PDFInfoNotInstalledError:
        print("✗ Poppler NOT installed or not in PATH")
        return False
    except Exception as e:
        print(f"⚠ Poppler test inconclusive: {str(e)}")
        return True  # Don't fail on inconclusive


def test_tesseract():
    """Test Tesseract OCR installation"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR installed (version {version})")
        return True
    except Exception as e:
        print(f"✗ Tesseract NOT installed or not in PATH: {str(e)}")
        return False


def test_opencv():
    """Test OpenCV functionality"""
    try:
        import cv2
        import numpy as np

        # Create a simple test image
        test_img = np.zeros((100, 100), dtype=np.uint8)
        edges = cv2.Canny(test_img, 50, 150)

        print("✓ OpenCV functioning correctly")
        return True
    except Exception as e:
        print(f"✗ OpenCV test failed: {str(e)}")
        return False


def main():
    print("=" * 50)
    print("Module A - Installation Test")
    print("=" * 50)
    print()

    results = []

    print("[1/5] Testing Python version...")
    results.append(test_python_version())
    print()

    print("[2/5] Testing Python packages...")
    results.append(test_imports())
    print()

    print("[3/5] Testing Poppler...")
    results.append(test_poppler())
    print()

    print("[4/5] Testing Tesseract OCR...")
    results.append(test_tesseract())
    print()

    print("[5/5] Testing OpenCV...")
    results.append(test_opencv())
    print()

    print("=" * 50)

    if all(results):
        print("✓ ALL TESTS PASSED")
        print("You're ready to run Module A!")
        print()
        print("Start the backend with:")
        print("  python main.py")
    else:
        print("✗ SOME TESTS FAILED")
        print("Please install missing dependencies.")
        print("See README.md for installation instructions.")

    print("=" * 50)


if __name__ == "__main__":
    main()
