# How to Start Module A

Simple step-by-step guide to get the application running.

---

## First Time Setup

### Step 1: Install System Dependencies

**Windows (using Chocolatey):**
```bash
# Install Chocolatey first if you don't have it:
# https://chocolatey.org/install

# Then install dependencies:
choco install poppler tesseract
```

**Or manually download:**
- Poppler: https://github.com/oschwartz10612/poppler-windows/releases
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

**macOS:**
```bash
brew install poppler tesseract
```

**Linux:**
```bash
sudo apt install poppler-utils tesseract-ocr
```

---

### Step 2: Setup Backend

Open a terminal in the project root:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate           # Windows
# OR
source venv/bin/activate        # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Test installation (optional but recommended)
python test_installation.py
```

---

### Step 3: Setup Frontend

Open a **NEW** terminal in the project root:

```bash
cd frontend

# Install dependencies
npm install
```

---

## Starting the Application (Every Time)

### Terminal 1 - Start Backend

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate           # Windows
# OR
source venv/bin/activate        # macOS/Linux

# Start server
python main.py
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Leave this terminal running!**

---

### Terminal 2 - Start Frontend

In a **NEW** terminal:

```bash
cd frontend

# Start development server
npm run dev
```

**You should see:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

**Leave this terminal running too!**

---

## Access the Application

Open your browser and go to:

**http://localhost:3000**

---

## Running Your First Test

1. **Click** the upload area or **drag** a PDF file
2. **Select**: `Resources/25-024 Home Sweet Home Preliminary Plans_11.18.2025.pdf`
3. **Click** "Process PDF"
4. **Wait** 30-60 seconds (watch Terminal 1 for progress)
5. **View** results:
   - Total impervious/pervious areas
   - Surface type breakdown
   - Individual polygon list
6. **Download** CSV for further analysis

---

## Stopping the Application

Press `Ctrl + C` in both terminal windows.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "python not found" | Install Python 3.9+ from python.org |
| "npm not found" | Install Node.js 16+ from nodejs.org |
| "Poppler not found" | Install Poppler and add to PATH |
| "Backend won't start" | Check venv is activated |
| "Port 8000 in use" | Stop other apps using port 8000 |
| "Port 3000 in use" | Frontend will offer port 3001 |
| "Connection error" | Ensure backend is running first |

---

## Quick Start Commands

**Using convenience scripts:**

```bash
# Windows
start_backend.bat       # Terminal 1
start_frontend.bat      # Terminal 2

# macOS/Linux
./start_backend.sh      # Terminal 1
./start_frontend.sh     # Terminal 2
```

---

## What's Happening Behind the Scenes

When you upload a PDF:

1. **Frontend** sends file to backend via HTTP
2. **Backend** converts PDF pages to images (300 DPI)
3. **OpenCV** detects edges and polygons
4. **Classifier** analyzes hatch patterns
5. **Scaler** detects scale bars
6. **Calculator** computes areas in square feet
7. **Exporter** generates CSV/GeoJSON
8. **Frontend** displays results

---

## Need Help?

- Check `README.md` for detailed documentation
- Run `python backend/test_installation.py` to verify dependencies
- Check terminal output for error messages
- Ensure both terminals stay open while using the app

---

**Ready? Let's start it up!**
