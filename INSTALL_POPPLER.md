# Quick Poppler Installation Guide

You're seeing this error: "Unable to get page count. Is poppler installed and in PATH?"

## Option 1: Install via Winget (Fastest)

Open a **new** PowerShell/Command Prompt window:

```bash
winget install sharkdp.poppler
```

Then restart your backend server.

---

## Option 2: Manual Download (If winget doesn't work)

### Step 1: Download Poppler

Go to: https://github.com/oschwartz10612/poppler-windows/releases/latest

Download: **Release-XX.XX.X-X.zip** (latest version)

### Step 2: Extract

Extract the ZIP file to a permanent location, for example:
```
C:\Program Files\poppler
```

### Step 3: Add to PATH

1. Press `Windows Key` + type "environment variables"
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "System variables", find and select "Path"
5. Click "Edit"
6. Click "New"
7. Add: `C:\Program Files\poppler\Library\bin`
8. Click OK on all windows

### Step 4: Verify Installation

Open a **new** Command Prompt and run:
```bash
pdftoppm -h
```

You should see Poppler's help text.

### Step 5: Restart Backend

Stop the current backend (press Ctrl+C in the backend terminal) and restart:
```bash
cd backend
venv\Scripts\activate
python main.py
```

---

## Quick Alternative: Use Chocolatey with Admin Rights

If you have admin access:

1. Open Command Prompt as **Administrator**
2. Run:
```bash
choco install poppler -y
```

---

## After Installation

Once Poppler is installed:

1. Keep frontend running (http://localhost:3000)
2. Restart backend server
3. Try uploading the PDF again

The PDF processing should now work!
