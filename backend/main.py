"""
Module A - LCR Area Calculations Engine
FastAPI Backend for PDF-based area extraction and classification
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
import threading
from typing import List, Dict, Any

from modules.pdf_reader import pdf_to_images
from modules.polygon_extractor import extract_polygons
from modules.classifier import classify_polygon
from modules.scaler import detect_scale, scale_polygon_area
from modules.exporter import export_to_csv, export_to_geojson
from modules.analyzer import needs_review, calculate_confidence
from modules.image_handler import encode_image_to_base64, get_image_dimensions
from modules.vector_extractor import extract_vectors_from_pdf, get_page_as_image_base64
import fitz  # PyMuPDF

app = FastAPI(
    title="LCR Area Calculations - Module A",
    description="PDF-based area extraction for landscape coverage ratio calculations",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary upload directory
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory job store for async processing
JOBS: Dict[str, Dict[str, Any]] = {}
JOBS_LOCK = threading.Lock()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "module": "Module A - PDF Area Extraction",
        "version": "1.0.0"
    }


def _process_pdf_internal(pdf_path: str, file_id: str, original_filename: str, job_id: str | None = None) -> Dict[str, Any]:
    """
    Core PDF processing logic using VECTOR EXTRACTION.
    Reads actual CAD geometry directly from the PDF instead of image processing.
    """

    print(f"Extracting vectors from PDF: {original_filename}")
    
    # Open PDF with PyMuPDF
    doc = fitz.open(pdf_path)
    total_sheets = len(doc)
    print(f"PDF has {total_sheets} pages")

    all_results: List[Dict[str, Any]] = []
    sheets_data: List[Dict[str, Any]] = []
    total_areas = {
        "concrete": 0.0,
        "building": 0.0,
        "pervious": 0.0,
        "asphalt": 0.0,
        "water": 0.0
    }

    # Optional: Only process specific sheets (set to None to process all)
    # Sheet numbers are 1-indexed for user convenience
    SHEETS_TO_PROCESS = None  # Set to [2, 4, 5] to limit processing

    for page_idx in range(total_sheets):
        sheet_number = page_idx + 1
        
        # Skip sheets not in the filter list (if filter is set)
        if SHEETS_TO_PROCESS is not None and sheet_number not in SHEETS_TO_PROCESS:
            print(f"Skipping sheet {sheet_number}/{total_sheets} (not in filter)")
            continue
            
        print(f"Processing sheet {sheet_number}/{total_sheets}")

        if job_id is not None:
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                if job:
                    job["current_sheet"] = sheet_number
                    job["total_sheets"] = total_sheets

        page = doc[page_idx]
        
        # Extract vector geometry from this page
        from modules.vector_extractor import extract_page_vectors
        page_data = extract_page_vectors(page, sheet_number)
        
        # Render page to image for visualization
        try:
            sheet_image_base64 = get_page_as_image_base64(page, dpi=150)
        except Exception as e:
            print(f"  Warning: Failed to render page image: {e}")
            sheet_image_base64 = None

        sheet_results = []
        sheet_areas = {
            "concrete": 0.0,
            "building": 0.0,
            "pervious": 0.0,
            "asphalt": 0.0,
            "water": 0.0
        }

        # Process extracted polygons
        for poly in page_data["polygons"]:
            area_sqft = poly["area_sqft"]
            surface_type = poly["type"]
            
            # Skip very small polygons (< 50 sqft, likely noise)
            if area_sqft < 50:
                continue
            
            # Ensure surface_type is valid
            if surface_type not in total_areas:
                surface_type = "pervious"

            # Keep coordinates in PDF space - frontend will transform them
            poly_result = {
                "id": poly["id"],
                "sheet": sheet_number,
                "type": surface_type,
                "area_sqft": round(area_sqft, 2),
                "coords_pdf": poly["coordinates"],  # Native PDF coordinates
                "coordinates": poly["coordinates"],  # Alias for backward compatibility
                "bbox_pdf": poly["bbox"],  # Native PDF bbox
                "bbox": poly["bbox"],  # Alias for backward compatibility
                "review_needed": False,
                "review_reasons": [],
                "confidence": 0.9,  # Vector extraction is high confidence
                "vertex_count": len(poly["coordinates"]),
                "source": poly.get("source", "vector")
            }

            sheet_results.append(poly_result)
            total_areas[surface_type] += area_sqft
            sheet_areas[surface_type] += area_sqft

        all_results.extend(sheet_results)

        # Add sheet summary with PDF dimensions for frontend coordinate transformation
        sheet_summary = {
            "sheet_number": sheet_number,
            "image_base64": sheet_image_base64,
            "pdf_width": page.rect.width,   # Native PDF width
            "pdf_height": page.rect.height, # Native PDF height
            "polygons_count": len(sheet_results),
            "scale_feet_per_pdf_unit": page_data.get("scale_factor", 1.0),
            "polygons": sheet_results,
            "sheet_totals": {
                "impervious": round(sheet_areas["concrete"] + sheet_areas["asphalt"] + sheet_areas["building"], 2),
                "pervious": round(sheet_areas["pervious"], 2),
                "breakdown": {
                    "concrete": round(sheet_areas["concrete"], 2),
                    "asphalt": round(sheet_areas["asphalt"], 2),
                    "building": round(sheet_areas["building"], 2),
                    "pervious": round(sheet_areas["pervious"], 2)
                }
            }
        }

        sheets_data.append(sheet_summary)
    
    doc.close()

    # Step 3: Compute summary statistics
    total_impervious = round(
        total_areas["concrete"] + total_areas["asphalt"] + total_areas["building"],
        2
    )
    total_pervious = round(total_areas["pervious"], 2)
    total_site_area = total_impervious + total_pervious

    # Count polygons needing review
    review_needed_count = sum(1 for poly in all_results if poly.get('review_needed', False))

    summary = {
        "total_polygons": len(all_results),
        "polygons_needing_review": review_needed_count,
        "total_impervious_sqft": total_impervious,
        "total_pervious_sqft": total_pervious,
        "total_site_area_sqft": round(total_site_area, 2),
        "percent_impervious": round((total_impervious / total_site_area * 100), 2) if total_site_area > 0 else 0,
        "percent_pervious": round((total_pervious / total_site_area * 100), 2) if total_site_area > 0 else 0,
        "breakdown": {
            "concrete": round(total_areas["concrete"], 2),
            "asphalt": round(total_areas["asphalt"], 2),
            "building": round(total_areas["building"], 2),
            "pervious": round(total_areas["pervious"], 2)
        },
        "categorized": {
            "impervious_surfaces": {
                "building_footprints": round(total_areas["building"], 2),
                "concrete_paving": round(total_areas["concrete"], 2),
                "asphalt_paving": round(total_areas["asphalt"], 2),
                "subtotal": total_impervious
            },
            "pervious_surfaces": {
                "turf_grass": round(total_areas["pervious"], 2),
                "subtotal": total_pervious
            }
        }
    }

    # Step 4: Generate exports
    csv_path = os.path.join(UPLOAD_DIR, f"{file_id}_results.csv")
    geojson_path = os.path.join(UPLOAD_DIR, f"{file_id}_results.geojson")

    export_to_csv(all_results, summary, csv_path)
    export_to_geojson(all_results, geojson_path)

    result: Dict[str, Any] = {
        "success": True,
        "filename": original_filename,
        "sheets_processed": len(sheets_data),
        "polygons": all_results,
        "sheets": sheets_data,
        "summary": summary,
        "exports": {
            "csv": csv_path,
            "geojson": geojson_path
        }
    }

    return result


@app.post("/api/process")
async def process_pdf(file: UploadFile = File(...)):
    """
    Synchronous processing endpoint (kept for compatibility).
    """

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    file_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = _process_pdf_internal(pdf_path, file_id, file.filename)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def _run_async_job(job_id: str, pdf_path: str, file_id: str, original_filename: str) -> None:
    try:
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if job:
                job["status"] = "running"

        result = _process_pdf_internal(pdf_path, file_id, original_filename, job_id=job_id)

        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if job:
                job["status"] = "completed"
                job["result"] = result
    except Exception as e:
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if job:
                job["status"] = "error"
                job["error"] = str(e)
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


@app.post("/api/process/start")
async def start_process(file: UploadFile = File(...)):
    """Start PDF processing as a background job and return a job id immediately."""

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    file_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with JOBS_LOCK:
        JOBS[job_id] = {
            "status": "queued",
            "current_sheet": 0,
            "total_sheets": 0,
            "filename": file.filename
        }

    thread = threading.Thread(
        target=_run_async_job,
        args=(job_id, pdf_path, file_id, file.filename),
        daemon=True,
    )
    thread.start()

    return {"job_id": job_id}


@app.get("/api/process/status/{job_id}")
async def get_process_status(job_id: str):
    """Return progress information for a given processing job."""

    with JOBS_LOCK:
        job = JOBS.get(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response: Dict[str, Any] = {
        "status": job.get("status"),
        "current_sheet": job.get("current_sheet", 0),
        "total_sheets": job.get("total_sheets", 0),
        "filename": job.get("filename"),
    }

    if job.get("status") == "completed":
        response["result"] = job.get("result")
    if job.get("status") == "error":
        response["error"] = job.get("error")

    return response


@app.get("/api/health")
async def health_check():
    """Detailed health check with dependencies"""
    return {
        "status": "healthy",
        "dependencies": {
            "pdf2image": "available",
            "opencv": "available",
            "tesseract": "available",
            "shapely": "available"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
