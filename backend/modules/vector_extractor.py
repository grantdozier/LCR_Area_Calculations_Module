"""
Vector Extraction Module
Extracts actual CAD geometry directly from PDF vector data.
This is the correct approach for engineering plans exported from Civil3D/AutoCAD.
"""

import fitz  # PyMuPDF
from shapely.geometry import Polygon, LineString, MultiLineString, box
from shapely.ops import polygonize, unary_union
from shapely.validation import make_valid
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict


def extract_vectors_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract vector geometry from all pages of a PDF.
    
    Returns a list of sheet data, each containing:
    - page_number
    - polygons: list of extracted polygon geometries
    - scale_factor: PDF units to feet conversion (if detected)
    """
    
    doc = fitz.open(pdf_path)
    all_sheets = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"  Extracting vectors from page {page_num + 1}...")
        
        sheet_data = extract_page_vectors(page, page_num + 1)
        all_sheets.append(sheet_data)
    
    doc.close()
    return all_sheets


def extract_page_vectors(page: fitz.Page, page_number: int) -> Dict[str, Any]:
    """
    Extract all vector paths from a single PDF page and convert to polygons.
    """
    
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height
    
    # Get all drawings (vector paths) from the page
    drawings = page.get_drawings()
    print(f"    Found {len(drawings)} drawing objects")
    
    # Collect all paths
    all_lines = []
    all_rects = []
    filled_paths = []
    closed_paths = []  # Paths that form closed loops (even without fill)
    
    for drawing in drawings:
        fill_color = drawing.get("fill")
        stroke_color = drawing.get("color")
        items = drawing.get("items", [])
        closePath = drawing.get("closePath", False)
        
        path_points = []
        current_path_lines = []
        
        for item in items:
            cmd = item[0]
            
            if cmd == "l":  # Line segment
                p1, p2 = item[1], item[2]
                all_lines.append(((p1.x, p1.y), (p2.x, p2.y)))
                current_path_lines.append(((p1.x, p1.y), (p2.x, p2.y)))
                path_points.extend([(p1.x, p1.y), (p2.x, p2.y)])
                
            elif cmd == "re":  # Rectangle
                rect = item[1]
                all_rects.append({
                    "bounds": (rect.x0, rect.y0, rect.x1, rect.y1),
                    "fill": fill_color,
                    "stroke": stroke_color
                })
                
            elif cmd == "c":  # Bezier curve - approximate with line segments
                points = item[1:]
                for i in range(len(points) - 1):
                    p1, p2 = points[i], points[i + 1]
                    if hasattr(p1, 'x'):
                        all_lines.append(((p1.x, p1.y), (p2.x, p2.y)))
                        current_path_lines.append(((p1.x, p1.y), (p2.x, p2.y)))
                        path_points.extend([(p1.x, p1.y), (p2.x, p2.y)])
                        
            elif cmd == "m":  # Move to
                p = item[1]
                path_points.append((p.x, p.y))
                
            elif cmd == "qu":  # Quadratic curve
                points = item[1:]
                for i in range(len(points) - 1):
                    p1, p2 = points[i], points[i + 1]
                    if hasattr(p1, 'x'):
                        all_lines.append(((p1.x, p1.y), (p2.x, p2.y)))
                        current_path_lines.append(((p1.x, p1.y), (p2.x, p2.y)))
        
        # If this path has a fill, it's likely a meaningful polygon
        if fill_color is not None and len(path_points) >= 3:
            filled_paths.append({
                "points": path_points,
                "fill": fill_color,
                "stroke": stroke_color
            })
        
        # Check if this is a closed path (building outlines, etc.)
        # Even without fill, closed paths are important
        if len(path_points) >= 4:
            # Check if first and last points are close (closed path)
            first = path_points[0]
            last = path_points[-1]
            dist = ((first[0] - last[0])**2 + (first[1] - last[1])**2)**0.5
            if dist < 5 or closePath:  # Within 5 PDF units = closed
                closed_paths.append({
                    "points": path_points,
                    "fill": fill_color,
                    "stroke": stroke_color
                })
    
    print(f"    Collected {len(all_lines)} lines, {len(all_rects)} rectangles, {len(filled_paths)} filled paths, {len(closed_paths)} closed paths")
    
    # Convert to Shapely geometries
    polygons = []
    
    # Process filled paths first (these are explicit polygons)
    for fp in filled_paths:
        try:
            if len(fp["points"]) >= 3:
                poly = Polygon(fp["points"])
                if poly.is_valid and poly.area > 100:  # Filter tiny shapes
                    polygons.append({
                        "geometry": poly,
                        "fill_color": fp["fill"],
                        "stroke_color": fp["stroke"],
                        "source": "filled_path"
                    })
        except Exception as e:
            pass
    
    # Process closed paths (building outlines, etc.)
    for cp in closed_paths:
        try:
            if len(cp["points"]) >= 4:
                # Remove duplicate consecutive points
                unique_points = [cp["points"][0]]
                for pt in cp["points"][1:]:
                    if pt != unique_points[-1]:
                        unique_points.append(pt)
                
                if len(unique_points) >= 3:
                    poly = Polygon(unique_points)
                    if not poly.is_valid:
                        poly = make_valid(poly)
                    if poly.is_valid and poly.area > 200:  # Slightly larger threshold
                        polygons.append({
                            "geometry": poly,
                            "fill_color": cp["fill"],
                            "stroke_color": cp["stroke"],
                            "source": "closed_path"
                        })
        except Exception as e:
            pass
    
    # Process rectangles
    for rect_data in all_rects:
        try:
            x0, y0, x1, y1 = rect_data["bounds"]
            poly = box(x0, y0, x1, y1)
            if poly.area > 100:
                polygons.append({
                    "geometry": poly,
                    "fill_color": rect_data["fill"],
                    "stroke_color": rect_data["stroke"],
                    "source": "rectangle"
                })
        except Exception as e:
            pass
    
    # Try to form polygons from line segments using polygonize
    if all_lines:
        try:
            line_strings = [LineString(line) for line in all_lines if line[0] != line[1]]
            # Merge nearby lines
            merged = unary_union(line_strings)
            # Attempt to form polygons from closed line loops
            formed_polys = list(polygonize(merged))
            
            print(f"    Formed {len(formed_polys)} polygons from line segments")
            
            for poly in formed_polys:
                if poly.is_valid and poly.area > 500:  # Larger threshold for line-formed polys
                    polygons.append({
                        "geometry": poly,
                        "fill_color": None,
                        "stroke_color": None,
                        "source": "polygonized_lines"
                    })
        except Exception as e:
            print(f"    Warning: polygonize failed: {e}")
    
    # Filter and deduplicate polygons
    filtered_polygons = filter_polygons(polygons, page_width, page_height)
    
    # Detect scale from the page
    scale_factor = detect_scale_from_vectors(page)
    
    # Convert to output format
    output_polygons = []
    for idx, poly_data in enumerate(filtered_polygons):
        geom = poly_data["geometry"]
        
        # Get coordinates
        if hasattr(geom.exterior, 'coords'):
            coords = list(geom.exterior.coords)
        else:
            continue
        
        # Calculate area in PDF units
        pdf_area = geom.area
        
        # Convert to square feet if we have a scale
        if scale_factor:
            area_sqft = pdf_area * (scale_factor ** 2)
        else:
            area_sqft = pdf_area  # Raw PDF units
        
        # Classify based on fill color and geometry
        surface_type = classify_polygon(poly_data, geom)
        
        output_polygons.append({
            "id": f"page{page_number}_poly{idx}",
            "coordinates": [[round(c[0], 2), round(c[1], 2)] for c in coords],
            "area_pdf_units": round(pdf_area, 2),
            "area_sqft": round(area_sqft, 2),
            "type": surface_type,
            "fill_color": poly_data.get("fill_color"),
            "source": poly_data.get("source"),
            "bbox": {
                "x": round(geom.bounds[0], 2),
                "y": round(geom.bounds[1], 2),
                "w": round(geom.bounds[2] - geom.bounds[0], 2),
                "h": round(geom.bounds[3] - geom.bounds[1], 2)
            }
        })
    
    # Count by type for debugging
    type_counts = {}
    for p in output_polygons:
        t = p["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"    Extracted {len(output_polygons)} valid polygons: {type_counts}")
    
    return {
        "page_number": page_number,
        "page_width": page_width,
        "page_height": page_height,
        "scale_factor": scale_factor,
        "polygons": output_polygons
    }


def filter_polygons(
    polygons: List[Dict], 
    page_width: float, 
    page_height: float,
    min_area_ratio: float = 0.0001,
    max_area_ratio: float = 0.6  # Increased to allow larger features like buildings
) -> List[Dict]:
    """
    Filter out noise and border polygons.
    """
    
    page_area = page_width * page_height
    min_area = page_area * min_area_ratio
    max_area = page_area * max_area_ratio
    
    filtered = []
    seen_bounds = set()
    
    for poly_data in polygons:
        geom = poly_data["geometry"]
        area = geom.area
        
        # Area filters
        if area < min_area or area > max_area:
            continue
        
        # Dimension filters (reject things spanning full page - likely borders)
        bounds = geom.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        # Only reject if BOTH dimensions are very large (actual page border)
        if width > page_width * 0.95 and height > page_height * 0.95:
            continue
        
        # Aspect ratio filter (reject very thin shapes - likely lines)
        aspect = max(width, height) / (min(width, height) + 0.1)
        if aspect > 30:  # Relaxed from 20
            continue
        
        # Deduplicate by bounds (with coarser rounding to catch near-duplicates)
        bounds_key = (round(bounds[0], 0), round(bounds[1], 0), 
                      round(bounds[2], 0), round(bounds[3], 0))
        if bounds_key in seen_bounds:
            continue
        seen_bounds.add(bounds_key)
        
        filtered.append(poly_data)
    
    return filtered


def detect_scale_from_vectors(page: fitz.Page) -> Optional[float]:
    """
    Attempt to detect the scale factor from graphic scale bars on the page.
    Returns feet per PDF unit, or None if not detected.
    """
    
    # Look for text containing scale information
    text = page.get_text()
    
    # Common scale patterns in civil plans
    import re
    
    # Pattern: "1" = 20'" or "SCALE: 1"=20'"
    scale_match = re.search(r'1["\']?\s*=\s*(\d+)["\']?', text)
    if scale_match:
        feet_per_inch = int(scale_match.group(1))
        # PDF default is 72 points per inch
        # So 1 inch on paper = feet_per_inch actual feet
        # PDF units per foot = 72 / feet_per_inch
        pdf_units_per_foot = 72 / feet_per_inch
        feet_per_pdf_unit = 1 / pdf_units_per_foot
        print(f"    Detected scale: 1\" = {feet_per_inch}' ({feet_per_pdf_unit:.4f} ft/PDF unit)")
        return feet_per_pdf_unit
    
    # Try to find graphic scale bar (e.g., "0 40 80 Feet")
    scale_bar_match = re.search(r'(\d+)\s+(\d+)\s+(\d+)?\s*(?:FEET|FT|\')', text, re.IGNORECASE)
    if scale_bar_match:
        # This gives us the labeled distances, but we'd need to measure the bar length
        # For now, use a reasonable default for civil plans
        pass
    
    # Default assumption for civil site plans at 1"=20' scale
    # This is very common for site plans
    default_scale = 20  # feet per inch
    pdf_units_per_foot = 72 / default_scale
    feet_per_pdf_unit = 1 / pdf_units_per_foot
    print(f"    Using default scale assumption: 1\" = {default_scale}' ({feet_per_pdf_unit:.4f} ft/PDF unit)")
    
    return feet_per_pdf_unit


def classify_polygon(poly_data: Dict, geom: Polygon) -> str:
    """
    Classify a polygon based on its properties.
    Uses fill color, shape metrics, and area to determine surface type.
    """
    
    fill = poly_data.get("fill_color")
    source = poly_data.get("source")
    
    # Calculate shape metrics
    area = geom.area
    perimeter = geom.length
    bounds = geom.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    
    # Rectangularity (how close to a rectangle)
    rect_area = width * height
    rectangularity = area / rect_area if rect_area > 0 else 0
    
    # Compactness (circle = 1, complex shapes < 1)
    compactness = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
    
    # Number of vertices (simplified polygon)
    num_vertices = len(list(geom.exterior.coords)) - 1  # -1 because first=last
    
    # Classification logic based on fill color
    if fill:
        if isinstance(fill, tuple) and len(fill) >= 3:
            r, g, b = fill[0], fill[1], fill[2]
            
            # Very dark (black) = typically building or heavy structure
            if r < 0.2 and g < 0.2 and b < 0.2:
                return "building"
            
            # Dark gray = asphalt
            if r < 0.4 and g < 0.4 and b < 0.4 and abs(r - g) < 0.1:
                return "asphalt"
            
            # Medium gray = concrete
            if 0.4 <= r <= 0.85 and abs(r - g) < 0.15 and abs(r - b) < 0.15:
                return "concrete"
            
            # Light gray (near white) = could be concrete or building
            if r > 0.85 and g > 0.85 and b > 0.85:
                if rectangularity > 0.85 and num_vertices <= 6:
                    return "building"
                return "concrete"
            
            # Green tint = pervious/grass
            if g > r * 1.1 and g > b * 1.1:
                return "pervious"
            
            # Blue tint = water/pond
            if b > r * 1.2 and b > g * 1.1:
                return "water"
            
            # Red/brown tint = could be building
            if r > g * 1.2 and r > b * 1.2:
                return "building"
    
    # Shape-based classification (when no fill color)
    # Highly rectangular with few vertices = likely building
    if rectangularity > 0.88 and num_vertices <= 8:
        # Large rectangular shapes are likely buildings
        if area > 1000:  # Significant size in PDF units
            return "building"
        return "concrete"
    
    # Moderately rectangular = concrete/paving
    if rectangularity > 0.6:
        return "concrete"
    
    # Compact shapes could be various things
    if compactness > 0.7:
        return "concrete"
    
    # Default to pervious for irregular/organic shapes
    return "pervious"


def get_page_as_image_base64(page: fitz.Page, dpi: int = 150) -> str:
    """
    Render a PDF page to a base64-encoded PNG image.
    """
    import base64
    
    # Render page to pixmap
    zoom = dpi / 72  # 72 is default PDF DPI
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to PNG bytes
    png_bytes = pix.tobytes("png")
    
    # Encode to base64
    b64 = base64.b64encode(png_bytes).decode('utf-8')
    
    return f"data:image/png;base64,{b64}"
