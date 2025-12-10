"""
Surface Classifier Module
Classifies polygons based on hatch patterns and pixel intensity

Classification Rules (V1 - Simple Heuristic):
- Dark diagonal hatch → Building footprint
- Dense speckled hatch → Concrete/Asphalt
- Light/no hatch → Pervious (grass, landscape)

Future: Add ML model + OCR label anchoring
"""

import cv2
import numpy as np
from typing import Dict, Any


def classify_polygon(img_path: str, contour: np.ndarray) -> str:
    """
    Classify a polygon based on its interior pattern

    Args:
        img_path: Path to the source image
        contour: OpenCV contour representing the polygon

    Returns:
        Surface type: "building", "concrete", "asphalt", or "pervious"
    """

    # Load image
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Create mask for polygon region
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)

    # Extract region of interest
    roi = cv2.bitwise_and(gray, gray, mask=mask)

    # Calculate intensity statistics
    pixels = roi[mask == 255]
    if len(pixels) == 0:
        return "pervious"  # default

    mean_intensity = np.mean(pixels)
    std_intensity = np.std(pixels)

    # Analyze texture patterns using edge density
    edges = cv2.Canny(roi, 50, 150)
    edge_density = np.sum(edges[mask == 255]) / len(pixels) if len(pixels) > 0 else 0

    # Classification heuristics
    # These thresholds are derived from typical plan hatch patterns

    # Building footprints: diagonal hatching → high edge density, medium darkness
    if edge_density > 0.15 and 80 < mean_intensity < 180:
        return "building"

    # Concrete/Asphalt: dense speckled pattern → moderate intensity, high variance
    elif 100 < mean_intensity < 200 and std_intensity > 30:
        return "concrete"

    # Very dark areas with low variance → asphalt
    elif mean_intensity < 100 and std_intensity < 25:
        return "asphalt"

    # Light areas with low edge density → pervious (grass, landscaping)
    else:
        return "pervious"


def analyze_hatch_pattern(roi: np.ndarray) -> Dict[str, Any]:
    """
    Advanced hatch pattern analysis (for future ML integration)

    Analyzes:
    - Line angle distribution
    - Pattern spacing
    - Pattern regularity

    Args:
        roi: Region of interest (grayscale)

    Returns:
        Dictionary of pattern features
    """

    # Detect lines using Hough transform
    edges = cv2.Canny(roi, 50, 150)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=50,
        minLineLength=20,
        maxLineGap=5
    )

    if lines is None:
        return {
            "has_hatch": False,
            "dominant_angle": None,
            "line_count": 0
        }

    # Calculate line angles
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        angles.append(angle)

    angles = np.array(angles)

    return {
        "has_hatch": True,
        "dominant_angle": np.median(angles) if len(angles) > 0 else None,
        "line_count": len(lines),
        "angle_variance": np.std(angles) if len(angles) > 0 else 0
    }
