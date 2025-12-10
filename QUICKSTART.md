# Quick Start Guide

Get Module A running in 5 minutes.

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check Node.js (need 16+)
node --version

# Check if Poppler is installed
pdftoppm -h

# Check if Tesseract is installed
tesseract --version
```

If any are missing, see [README.md](README.md) Installation Guide.

---

## Setup (One-Time)

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

---

## Running the App

**Terminal 1 - Backend:**
```bash
cd backend
# Activate venv if not active
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Open:** http://localhost:3000

---

## First Test

1. Open the web app
2. Upload: `Resources/25-024 Home Sweet Home Preliminary Plans_11.18.2025.pdf`
3. Click "Process PDF"
4. Wait 30-60 seconds
5. View results and download CSV

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Backend won't start | Check venv is activated |
| "Poppler not found" | Install Poppler (see README) |
| Frontend connection error | Ensure backend running on port 8000 |
| Slow processing | Normal for first run, ~30-60s per PDF |

---

## Next Steps

- Review [README.md](README.md) for detailed documentation
- Test with your own plan set PDFs
- Check backend logs for processing details
- Experiment with different surface classifications

---

**Ready to build? Start processing!**
