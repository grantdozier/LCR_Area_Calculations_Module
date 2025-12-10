"""
Export Module
Exports processed area calculations to various formats

Formats:
- CSV: Tabular data for Excel/spreadsheet analysis
- GeoJSON: Geographic data for GIS/mapping tools
"""

import csv
import json
from typing import List, Dict, Any


def export_to_csv(polygons: List[Dict[str, Any]], summary: Dict[str, Any], output_path: str) -> None:
    """
    Export polygon results to CSV

    Args:
        polygons: List of polygon dictionaries
        summary: Summary statistics
        output_path: Path to save CSV file
    """

    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Header
        writer.writerow(['LCR Area Calculations - Module A'])
        writer.writerow([])

        # Summary section
        writer.writerow(['Summary'])
        writer.writerow(['Total Polygons', summary['total_polygons']])
        writer.writerow(['Total Impervious (sqft)', summary['total_impervious_sqft']])
        writer.writerow(['Total Pervious (sqft)', summary['total_pervious_sqft']])
        writer.writerow([])

        # Breakdown section
        writer.writerow(['Breakdown by Surface Type'])
        writer.writerow(['Concrete (sqft)', summary['breakdown']['concrete']])
        writer.writerow(['Asphalt (sqft)', summary['breakdown']['asphalt']])
        writer.writerow(['Building (sqft)', summary['breakdown']['building']])
        writer.writerow(['Pervious (sqft)', summary['breakdown']['pervious']])
        writer.writerow([])

        # Detailed polygon data
        writer.writerow(['Detailed Polygon Data'])
        writer.writerow(['Polygon ID', 'Sheet', 'Surface Type', 'Area (sqft)', 'Perimeter Type'])

        for poly in polygons:
            perimeter_type = 'Impervious' if poly['type'] in ['concrete', 'asphalt', 'building'] else 'Pervious'
            writer.writerow([
                poly['id'],
                poly['sheet'],
                poly['type'],
                poly['area_sqft'],
                perimeter_type
            ])

    print(f"  ✓ CSV exported to: {output_path}")


def export_to_geojson(polygons: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export polygon results to GeoJSON format

    Args:
        polygons: List of polygon dictionaries
        output_path: Path to save GeoJSON file
    """

    features = []

    for poly in polygons:
        # Convert coordinates to GeoJSON Polygon format
        # Note: GeoJSON requires [longitude, latitude], but we use pixel coords
        # In a real implementation, this would need georeferencing

        # Support both old 'coordinates' and new 'coords_pdf' field names
        coords = poly.get('coords_pdf') or poly.get('coordinates', [])
        coordinates = [[coord for coord in coords]]

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            },
            "properties": {
                "id": poly['id'],
                "sheet": poly['sheet'],
                "surface_type": poly['type'],
                "area_sqft": poly['area_sqft'],
                "perimeter_type": "Impervious" if poly['type'] in ['concrete', 'asphalt', 'building'] else "Pervious"
            }
        }

        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)

    print(f"  ✓ GeoJSON exported to: {output_path}")


def export_to_toc_format(polygons: List[Dict[str, Any]], summary: Dict[str, Any], output_path: str) -> None:
    """
    Export to Time of Concentration (TOC) calculation format

    This format is specific to LADOTD drainage calculations
    Future integration with TOC spreadsheet template

    Args:
        polygons: List of polygon dictionaries
        summary: Summary statistics
        output_path: Path to save file
    """

    toc_data = {
        "project_info": {
            "module": "Module A - Area Calculations",
            "total_site_area_sqft": summary['total_impervious_sqft'] + summary['total_pervious_sqft'],
            "impervious_area_sqft": summary['total_impervious_sqft'],
            "pervious_area_sqft": summary['total_pervious_sqft']
        },
        "surface_breakdown": summary['breakdown'],
        "runoff_coefficients": {
            "concrete": 0.90,  # From LADOTD Hydraulics Manual Table 3-C.3-1
            "asphalt": 0.90,
            "building": 0.90,
            "pervious": 0.20  # Average for grass/landscape
        },
        "polygons": polygons
    }

    with open(output_path, 'w') as f:
        json.dump(toc_data, f, indent=2)

    print(f"  ✓ TOC format exported to: {output_path}")
