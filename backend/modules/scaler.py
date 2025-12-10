"""
Scale Detection and Conversion Module
Detects scale bars on plan sheets and converts pixel measurements to real-world units

Typical scale bar format: "Feet 0 20 40" or "0' 20' 40'"
Target: Extract pixels_per_foot ratio for accurate area calculations
"""

import os
import cv2
import numpy as np
import pytesseract
import re
from typing import Optional, Tuple


# Configure Tesseract executable on Windows if installed in default location
TESSERACT_WIN_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
if os.path.exists(TESSERACT_WIN_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_WIN_PATH


def detect_scale(img_path: str) -> float:
    """
    Detect the scale bar and compute pixels per foot

    Strategy:
    1. OCR scan for "Feet", "0", "20", "40" or similar patterns
    2. Locate scale bar graphically (horizontal line with tick marks)
    3. Measure pixel distance between "0" and known distance (e.g., 20 or 40)
    4. Return pixels_per_foot

    Args:
        img_path: Path to the plan sheet image

    Returns:
        pixels_per_foot ratio
    """

    print("  Detecting scale bar...")

    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Strategy 1: OCR-based scale detection (used only as a secondary hint)
    ocr_scale_ratio: Optional[float] = None
    try:
        # Focus on bottom 20% of image where scale bars are typically located
        h, w = gray.shape
        roi = gray[int(h * 0.8):, :]

        # OCR with pytesseract
        ocr_text = pytesseract.image_to_string(roi, config='--psm 6')
        print(f"  OCR detected: {ocr_text[:100]}")

        # Parse scale text
        ocr_scale_ratio = parse_scale_text(ocr_text)

        if ocr_scale_ratio is not None:
            print(f"  ✓ Scale hinted from OCR: {ocr_scale_ratio:.2f} pixels/foot")

    except Exception as e:
        print(f"  OCR scale detection failed: {str(e)}")

    # Strategy 2: Graphical scale bar detection
    print("  Attempting graphical scale detection...")
    scale_ratio = detect_scale_bar_graphically(gray)

    if scale_ratio is not None:
        print(f"  ✓ Scale detected graphically: {scale_ratio:.2f} pixels/foot")
        return scale_ratio

    # If graphical detection fails but OCR returned something large enough,
    # use it as a fallback. Very small values (like the 15 px/ft placeholder)
    # are rejected because they produce wildly incorrect areas.
    if ocr_scale_ratio is not None and ocr_scale_ratio > 50:
        print(f"  ⚠ Using OCR-only scale estimate: {ocr_scale_ratio:.2f} pixels/foot")
        return ocr_scale_ratio

    # Fallback: Use typical architectural scale (1" = 20')
    print("  ⚠ Scale bar not found, using fallback: 1\" = 20' at 300 DPI")
    # At 300 DPI: 1 inch = 300 pixels, 20 feet → 300 pixels
    fallback_ratio = 300 / 20  # 15 pixels/foot
    return fallback_ratio


def parse_scale_text(text: str) -> Optional[float]:
    """
    Parse OCR text to extract scale ratio

    Looks for patterns like:
    - "0 20 40" (numeric scale)
    - "Feet 0 20 40"
    - "0' 20' 40'"

    Args:
        text: OCR text output

    Returns:
        pixels_per_foot if found, else None
    """

    # Clean text
    text = text.replace('\n', ' ').lower()

    # Pattern 1: "feet 0 20 40" or "0 20 40"
    pattern1 = re.search(r'feet.*?0.*?(\d+).*?(\d+)', text)
    if pattern1:
        # Assumes first number after 0 is the scale unit (e.g., 20 feet)
        scale_feet = int(pattern1.group(1))
        print(f"  Found scale pattern: 0-{scale_feet} feet")

        # TODO: Measure pixel distance (requires geometric detection)
        # For now, estimate based on typical engineering drawings at 300 DPI
        # Typical: 1" = 20' → 300px = 20ft → 15 px/ft
        return 15.0  # Placeholder

    return None


def detect_scale_bar_graphically(gray: np.ndarray) -> Optional[float]:
    """
    Detect scale bar by finding horizontal lines with tick marks

    Args:
        gray: Grayscale image

    Returns:
        pixels_per_foot if detected, else None
    """

    h, w = gray.shape

    # Focus on bottom region
    roi = gray[int(h * 0.85):, :]

    # Detect horizontal lines
    edges = cv2.Canny(roi, 50, 150)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=100,
        minLineLength=100,
        maxLineGap=10
    )

    if lines is None:
        return None

    # Find longest horizontal line (likely the scale bar)
    max_length = 0
    scale_line = None

    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Check if line is approximately horizontal
        angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        if angle < 5 and length > max_length:
            max_length = length
            scale_line = line[0]

    if scale_line is not None:
        # Assume typical scale: 0-40 feet for engineering site plans
        # This is a simplification; real implementation would use OCR nearby
        assumed_feet = 40
        pixels_per_foot = max_length / assumed_feet
        return pixels_per_foot

    return None


def scale_polygon_area(pixel_area: float, pixels_per_foot: float) -> float:
    """
    Convert pixel area to square feet

    Args:
        pixel_area: Area in pixels²
        pixels_per_foot: Scale ratio

    Returns:
        Area in square feet
    """

    sqft_area = pixel_area / (pixels_per_foot ** 2)
    return sqft_area


def pixels_to_feet(pixel_distance: float, pixels_per_foot: float) -> float:
    """
    Convert pixel distance to feet

    Args:
        pixel_distance: Distance in pixels
        pixels_per_foot: Scale ratio

    Returns:
        Distance in feet
    """

    return pixel_distance / pixels_per_foot
