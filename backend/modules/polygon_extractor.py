"""
Polygon Extraction Module
Uses OpenCV to detect filled regions and closed polygons from plan sheet images.
Optimized for civil engineering site plans with hatching patterns.
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Tuple


def extract_polygons(img_path: str, min_area: int = 10000, max_area_ratio: float = 0.35) -> List[Dict[str, Any]]:
    """
    Extract meaningful polygons from a civil engineering plan sheet.
    
    Uses multiple detection strategies:
    1. Color/grayscale region segmentation (for filled areas)
    2. Morphological closing to merge hatching patterns into solid regions
    3. Contour detection with hierarchy filtering
    
    Args:
        img_path: Path to the image file
        min_area: Minimum polygon area in pixels (filters noise)
        max_area_ratio: Maximum polygon area as ratio of image area (filters borders/frames)

    Returns:
        List of polygon dictionaries containing contour data and metadata
    """

    print(f"  Extracting polygons from: {img_path}")

    # Read image
    img = cv2.imread(img_path)
    if img is None:
        raise Exception(f"Failed to load image: {img_path}")

    img_height, img_width = img.shape[:2]
    img_area = img_height * img_width
    max_area = img_area * max_area_ratio
    
    # Also filter out polygons that span nearly the full width or height (likely borders)
    max_dimension_ratio = 0.85
    max_width = img_width * max_dimension_ratio
    max_height = img_height * max_dimension_ratio

    all_polygons = []
    
    # Strategy 1: Detect filled/shaded regions by grayscale thresholding
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Find regions that are darker than the white background (filled areas, hatching)
    # Use adaptive thresholding to handle varying lighting/scan quality
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 10
    )
    
    # Heavy morphological closing to merge hatching patterns into solid regions
    # This is key for civil plans where areas are indicated by line patterns
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close, iterations=3)
    
    # Remove small noise
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_open, iterations=2)
    
    # Find contours - use RETR_EXTERNAL to get only outer boundaries
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"  Found {len(contours)} candidate regions after morphological processing")
    
    for idx, contour in enumerate(contours):
        polygon = _process_contour(contour, idx, min_area, max_area, max_width, max_height, "filled")
        if polygon:
            all_polygons.append(polygon)
    
    # Strategy 2: Detect rectangular structures (buildings) using edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Dilate edges to connect nearby lines
    kernel_dilate = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel_dilate, iterations=2)
    
    # Find contours from edges
    edge_contours, hierarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter for rectangular shapes (likely buildings)
    for idx, contour in enumerate(edge_contours):
        area = cv2.contourArea(contour)
        if area < min_area or area > max_area:
            continue
            
        # Check if it's roughly rectangular (building-like)
        rect = cv2.minAreaRect(contour)
        rect_area = rect[1][0] * rect[1][1]
        if rect_area > 0:
            rectangularity = area / rect_area
            # Only keep shapes that are fairly rectangular (> 70% fill of bounding rect)
            if rectangularity > 0.7:
                polygon = _process_contour(contour, len(all_polygons) + idx, min_area, max_area, max_width, max_height, "structure")
                if polygon and not _is_duplicate(polygon, all_polygons):
                    all_polygons.append(polygon)
    
    print(f"  Extracted {len(all_polygons)} valid polygons")
    
    return all_polygons


def _process_contour(
    contour: np.ndarray, 
    idx: int, 
    min_area: float, 
    max_area: float,
    max_width: float,
    max_height: float,
    detection_method: str
) -> Dict[str, Any] | None:
    """Process a single contour and return polygon data if valid."""
    
    area = cv2.contourArea(contour)
    
    # Filter by area
    if area < min_area or area > max_area:
        return None
    
    # Get bounding box and filter by dimensions
    x, y, w, h = cv2.boundingRect(contour)
    if w > max_width or h > max_height:
        return None
    
    # Filter out very thin shapes (likely lines or borders)
    aspect_ratio = max(w, h) / (min(w, h) + 1)
    if aspect_ratio > 15:  # Very elongated = probably a line
        return None
    
    # Approximate polygon to reduce vertices
    epsilon = 0.005 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # Extract polygon coordinates
    coordinates = []
    for point in approx:
        px, py = point[0]
        coordinates.append([int(px), int(py)])
    
    return {
        "contour": contour,
        "approx": approx,
        "pixel_area": area,
        "bbox": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
        "coordinates": coordinates,
        "vertex_count": len(approx),
        "detection_method": detection_method
    }


def _is_duplicate(new_polygon: Dict, existing_polygons: List[Dict], iou_threshold: float = 0.5) -> bool:
    """Check if a polygon significantly overlaps with any existing polygon."""
    
    new_bbox = new_polygon["bbox"]
    new_x1, new_y1 = new_bbox["x"], new_bbox["y"]
    new_x2, new_y2 = new_x1 + new_bbox["w"], new_y1 + new_bbox["h"]
    
    for existing in existing_polygons:
        ex_bbox = existing["bbox"]
        ex_x1, ex_y1 = ex_bbox["x"], ex_bbox["y"]
        ex_x2, ex_y2 = ex_x1 + ex_bbox["w"], ex_y1 + ex_bbox["h"]
        
        # Calculate intersection
        inter_x1 = max(new_x1, ex_x1)
        inter_y1 = max(new_y1, ex_y1)
        inter_x2 = min(new_x2, ex_x2)
        inter_y2 = min(new_y2, ex_y2)
        
        if inter_x2 > inter_x1 and inter_y2 > inter_y1:
            inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
            new_area = new_bbox["w"] * new_bbox["h"]
            
            # If intersection is > threshold of new polygon's area, it's a duplicate
            if inter_area / new_area > iou_threshold:
                return True
    
    return False
