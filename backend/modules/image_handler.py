"""
Image Handler Module
Handles image encoding and storage for frontend visualization
"""

import cv2
import base64
import numpy as np
from typing import Dict, Any, List
import os


def encode_image_to_base64(img_path: str, max_width: int = 1200) -> str:
    """
    Encode an image to base64 string for frontend transmission

    Args:
        img_path: Path to the image file
        max_width: Maximum width to resize to (for performance)

    Returns:
        Base64 encoded image string (data URL format)
    """

    img = cv2.imread(img_path)
    if img is None:
        raise Exception(f"Failed to load image: {img_path}")

    # Resize if too large
    height, width = img.shape[:2]
    if width > max_width:
        scale = max_width / width
        new_width = max_width
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Encode to JPEG
    success, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not success:
        raise Exception("Failed to encode image")

    # Convert to base64
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    return f"data:image/jpeg;base64,{jpg_as_text}"


def get_image_dimensions(img_path: str) -> Dict[str, int]:
    """
    Get image dimensions without loading entire image

    Args:
        img_path: Path to the image file

    Returns:
        Dictionary with width and height
    """

    img = cv2.imread(img_path)
    if img is None:
        return {"width": 0, "height": 0}

    height, width = img.shape[:2]
    return {"width": int(width), "height": int(height)}


def draw_polygon_overlay(img_path: str, polygons: List[Dict[str, Any]], output_path: str) -> str:
    """
    Draw colored polygons on the image for visualization

    Args:
        img_path: Path to the source image
        polygons: List of polygon data with coordinates and types
        output_path: Path to save the output image

    Returns:
        Path to the output image
    """

    # Color mapping for surface types (BGR format)
    COLOR_MAP = {
        "building": (0, 0, 200),      # Red
        "concrete": (128, 128, 128),  # Gray
        "asphalt": (50, 50, 50),      # Dark Gray
        "pervious": (0, 200, 0)       # Green
    }

    img = cv2.imread(img_path)
    if img is None:
        raise Exception(f"Failed to load image: {img_path}")

    overlay = img.copy()

    # Draw each polygon
    for poly in polygons:
        coords = np.array(poly['coordinates'], dtype=np.int32)
        color = COLOR_MAP.get(poly['type'], (255, 255, 255))

        # Draw filled polygon with transparency
        cv2.fillPoly(overlay, [coords], color)

        # Draw outline
        cv2.polylines(overlay, [coords], isClosed=True, color=color, thickness=2)

    # Blend with original image (50% transparency)
    result = cv2.addWeighted(img, 0.5, overlay, 0.5, 0)

    # Save result
    cv2.imwrite(output_path, result)

    return output_path
