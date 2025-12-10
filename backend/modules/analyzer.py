"""
Polygon Analyzer Module
Analyzes polygons for quality issues and generates review flags
"""

import numpy as np
from typing import Dict, Any, List
import cv2


def calculate_compactness(contour: np.ndarray) -> float:
    """
    Calculate polygon compactness (circularity measure)
    Values close to 1.0 = circular, lower values = irregular

    Formula: 4π * area / perimeter²
    """
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    if perimeter == 0:
        return 0.0

    compactness = (4 * np.pi * area) / (perimeter ** 2)
    return compactness


def needs_review(polygon_data: Dict[str, Any], area_sqft: float, all_areas: List[float]) -> Dict[str, Any]:
    """
    Determine if a polygon needs manual review

    Args:
        polygon_data: Polygon data dictionary from polygon_extractor
        area_sqft: Calculated area in square feet
        all_areas: List of all polygon areas for outlier detection

    Returns:
        Dictionary with review_needed flag and reasons
    """

    review_flags = []

    # 1. Check for extremely small areas (< 100 sqft)
    if area_sqft < 100:
        review_flags.append("Very small area")

    # 2. Check for extremely large areas (> 50,000 sqft)
    if area_sqft > 50000:
        review_flags.append("Very large area")

    # 3. Check for irregular shapes using compactness
    compactness = calculate_compactness(polygon_data['contour'])
    if compactness < 0.15:  # Very irregular
        review_flags.append("Irregular shape")

    # 4. Check for excessive vertices (overly complex polygon)
    if polygon_data['vertex_count'] > 50:
        review_flags.append("Complex polygon")

    # 5. Statistical outlier detection (if enough data)
    if len(all_areas) > 10:
        mean_area = np.mean(all_areas)
        std_area = np.std(all_areas)

        # Flag if area is more than 3 standard deviations from mean
        if abs(area_sqft - mean_area) > 3 * std_area:
            review_flags.append("Statistical outlier")

    return {
        "review_needed": len(review_flags) > 0,
        "review_reasons": review_flags,
        "compactness": round(compactness, 3)
    }


def calculate_confidence(polygon_data: Dict[str, Any], classification_metrics: Dict[str, float]) -> float:
    """
    Calculate classification confidence score (0.0 to 1.0)

    Args:
        polygon_data: Polygon data
        classification_metrics: Metrics from the classifier (intensity, edge_density, etc.)

    Returns:
        Confidence score between 0.0 and 1.0
    """

    confidence_factors = []

    # Factor 1: Compactness (irregular shapes = lower confidence)
    compactness = calculate_compactness(polygon_data['contour'])
    if compactness > 0.5:
        confidence_factors.append(0.9)
    elif compactness > 0.3:
        confidence_factors.append(0.7)
    else:
        confidence_factors.append(0.5)

    # Factor 2: Vertex count (simpler = higher confidence)
    vertex_count = polygon_data['vertex_count']
    if vertex_count < 10:
        confidence_factors.append(0.9)
    elif vertex_count < 30:
        confidence_factors.append(0.75)
    else:
        confidence_factors.append(0.6)

    # Factor 3: Area size (mid-range = higher confidence)
    pixel_area = polygon_data['pixel_area']
    if 5000 < pixel_area < 500000:
        confidence_factors.append(0.9)
    elif 1000 < pixel_area < 1000000:
        confidence_factors.append(0.75)
    else:
        confidence_factors.append(0.6)

    # Average all factors
    avg_confidence = np.mean(confidence_factors) if confidence_factors else 0.5

    return round(avg_confidence, 2)
