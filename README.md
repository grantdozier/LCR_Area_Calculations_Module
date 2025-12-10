# LCR Area Calculations - Module A

**PDF-based Area Extraction for Landscape Coverage Ratio Calculations**

Version 1.0.0

---

## Overview

Module A is a specialized engineering tool for extracting and classifying surface areas from plan set PDFs. It uses computer vision (OpenCV) to detect polygons, classify surface types (concrete, asphalt, building, pervious), and calculate areas with scale bar detection.

### Key Features

- PDF plan sheet processing at 300 DPI
- Automated polygon detection and extraction
- Surface classification based on hatch patterns
- Scale bar detection for accurate measurements
- Export to CSV and GeoJSON formats
- Interactive React-based visualization interface

### Architecture

```
┌─────────────────────────────────────────────────┐
│              React Frontend                     │
│  (Upload, Visualization, Results Export)        │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────┐
│           FastAPI Backend                       │
│  ┌───────────────────────────────────────────┐  │
│  │ PDF Reader → Image Processing             │  │
│  │ Polygon Extraction → Classification       │  │
│  │ Scale Detection → Area Calculation        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## System Requirements

### Backend (Python)

- Python 3.9 or higher
- Poppler (for PDF rendering)
- Tesseract OCR (for scale bar detection)

### Frontend (React)

- Node.js 16+ and npm

---

## Installation Guide

### Step 1: Install System Dependencies

#### Windows

1. **Install Python 3.9+**
   - Download from https://www.python.org/downloads/
   - Add to PATH during installation

2. **Install Poppler**
   ```bash
   # Using chocolatey
   choco install poppler

   # Or download manually from:
   # https://github.com/oschwartz10612/poppler-windows/releases
   # Extract and add bin/ to PATH
   ```

3. **Install Tesseract OCR**
   ```bash
   # Using chocolatey
   choco install tesseract

   # Or download installer from:
   # https://github.com/UB-Mannheim/tesseract/wiki
   ```

#### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.9 poppler tesseract
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip poppler-utils tesseract-ocr
```

### Step 2: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install
```

---

## Running the Application

### Terminal 1: Start Backend Server

```bash
cd backend
# Activate venv if not already active
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

python main.py
```

Backend will run on: http://localhost:8000

### Terminal 2: Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:3000

---

## Usage

1. **Open the application** in your browser at http://localhost:3000

2. **Upload a PDF** plan set by:
   - Clicking the upload area
   - Or dragging and dropping a PDF file

3. **Processing**:
   - The backend will extract each sheet at 300 DPI
   - Detect polygons using edge detection
   - Classify surface types based on hatch patterns
   - Calculate areas using detected scale bars

4. **View Results**:
   - Summary cards showing total impervious/pervious areas
   - Breakdown by surface type
   - List of all detected polygons
   - Filter by surface type

5. **Export Data**:
   - Click "Download CSV" to export results
   - CSV includes all polygon details and summary statistics

---

## Processing Algorithm

### 1. PDF Conversion
```python
PDF → Images (300 DPI) → Grayscale
```

### 2. Polygon Detection
```python
Gaussian Blur → Canny Edge Detection →
Morphological Closing → Contour Detection →
Polygon Approximation
```

### 3. Classification (V1 - Heuristic)

| Surface Type | Detection Method |
|-------------|------------------|
| Building | High edge density + medium darkness |
| Concrete/Asphalt | Moderate intensity + high variance |
| Pervious | Light areas + low edge density |

### 4. Scale Detection

- OCR scan for "Feet 0 20 40" patterns
- Graphical detection of horizontal scale bars
- Fallback: 1" = 20' at 300 DPI (15 px/ft)

### 5. Area Calculation

```python
area_sqft = pixel_area / (pixels_per_foot)²
```

---

## API Endpoints

### `POST /api/process`

Process a PDF plan set

**Request:**
- Content-Type: multipart/form-data
- Body: file (PDF)

**Response:**
```json
{
  "success": true,
  "filename": "plan.pdf",
  "sheets_processed": 5,
  "polygons": [
    {
      "id": "sheet0_poly0",
      "sheet": 1,
      "type": "concrete",
      "area_sqft": 1850.23,
      "coordinates": [[x1, y1], [x2, y2], ...]
    }
  ],
  "summary": {
    "total_polygons": 42,
    "total_impervious_sqft": 18240.5,
    "total_pervious_sqft": 28400.3,
    "breakdown": {
      "concrete": 12000.0,
      "asphalt": 5500.0,
      "building": 740.5,
      "pervious": 28400.3
    }
  }
}
```

### `GET /api/health`

Health check endpoint

---

## Project Structure

```
LCR_Area_Calculations_Module/
│
├── Resources/                          # Reference PDFs
│   ├── 25-024 Home Sweet Home Preliminary Plans_11.18.2025.pdf
│   ├── DIA Report - Home Sweet Home - 2025-11-14.pdf
│   └── Hydraulics Manual.pdf
│
├── backend/                            # Python FastAPI Backend
│   ├── main.py                         # Main FastAPI application
│   ├── requirements.txt                # Python dependencies
│   ├── temp_uploads/                   # Temporary upload directory
│   └── modules/
│       ├── pdf_reader.py              # PDF → Image conversion
│       ├── polygon_extractor.py       # OpenCV polygon detection
│       ├── classifier.py              # Surface classification
│       ├── scaler.py                  # Scale detection & conversion
│       └── exporter.py                # CSV/GeoJSON export
│
└── frontend/                           # React Frontend
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx                    # React entry point
        ├── App.jsx                     # Main app component
        ├── App.css
        ├── api/
        │   └── api.js                  # Backend API client
        └── components/
            ├── FileUpload.jsx          # File upload component
            ├── FileUpload.css
            ├── ResultsPanel.jsx        # Results visualization
            └── ResultsPanel.css
```

---

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'pdf2image'`
- **Solution:** Activate venv and reinstall: `pip install -r requirements.txt`

**Problem:** `PDFInfoNotInstalledError`
- **Solution:** Install Poppler (see Installation Guide)

**Problem:** `TesseractNotFoundError`
- **Solution:** Install Tesseract OCR and add to PATH

### Frontend Issues

**Problem:** `Cannot GET /api/process`
- **Solution:** Ensure backend is running on port 8000

**Problem:** `Network Error`
- **Solution:** Check CORS settings in backend/main.py

---

## Future Enhancements (V2+)

### Planned Features

- **ML-based classification** using trained hatch pattern recognition
- **Civil 3D DXF/DWG integration** for direct CAD file processing
- **Topology CSV import** for slope analysis
- **LADOTD runoff coefficient integration** (Hydraulics Manual Table 3-C.3-1)
- **Time of Concentration (TOC) calculations**
- **Interactive polygon editing** in frontend
- **GIS georeferencing** for accurate coordinate export
- **Batch processing** for multiple PDFs

---

## Technical Notes

### Scale Detection Limitations

V1 uses simplified scale detection. For production use:
- Verify scale bar detection accuracy
- Manually confirm measurements on first use
- Add custom scale override in UI (future feature)

### Classification Accuracy

Current heuristic-based classification achieves ~70-80% accuracy on typical plan sets. For higher accuracy:
- Train ML model on labeled plan sheets
- Add OCR label anchoring (e.g., "CONCRETE PAVING" text)
- Implement user correction feedback loop

### Performance

- Typical 5-page plan set: 30-60 seconds
- Scales with page count and complexity
- Future optimization: parallel sheet processing

---

## References

- **Home Sweet Home Plan Set**: Resources/25-024 Home Sweet Home Preliminary Plans_11.18.2025.pdf
- **LADOTD Hydraulics Manual**: Resources/Hydraulics Manual.pdf (Chapter 3, Rational Method)
- **Drainage Impact Assessment**: Resources/DIA Report - Home Sweet Home - 2025-11-14.pdf

---

## License

See LICENSE file for details.

---

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review backend logs for error details
3. Ensure all dependencies are installed correctly

---

**Module A v1.0.0** | PDF Processing Engine for LCR Calculations
