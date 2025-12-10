# Install Poppler - 2 Minute Guide

Your app is **almost working**! You just need Poppler installed.

## Fastest Method (Recommended)

### Step 1: Download Poppler

Click this link to download Poppler for Windows:
**https://github.com/oschwartz10612/poppler-windows/releases/download/v25.12.0-0/Release-25.12.0-0.zip**

Save it to your Downloads folder.

### Step 2: Extract

1. Go to your Downloads folder
2. Right-click `Release-25.12.0-0.zip`
3. Choose "Extract All..."
4. Extract to: `C:\poppler`

You should now have: `C:\poppler\Library\bin\`

### Step 3: Add to PATH (Windows 11/10)

**Quick method:**
1. Press `Windows Key` and type: **environment**
2. Click: **Edit the system environment variables**
3. Click: **Environment Variables** button (bottom right)
4. Under **System variables** (bottom section), find **Path**
5. Click **Edit**
6. Click **New**
7. Type: `C:\poppler\Library\bin`
8. Click **OK** three times

### Step 4: Verify

Open a **NEW** Command Prompt window and type:
```bash
pdftoppm -h
```

You should see Poppler help text.

### Step 5: Restart Backend

In your current terminal where the backend is running, press `Ctrl+C` to stop it.

Then restart:
```bash
cd backend
venv\Scripts\activate
python main.py
```

Keep the frontend running (it's fine).

### Step 6: Try Again

Go back to http://localhost:3000 and upload the PDF again!

---

## Alternative: Use Admin PowerShell

If you have admin rights, open PowerShell as Administrator:

```powershell
choco install poppler -y
```

Then restart the backend server.

---

## Still Stuck?

The error you're getting means the Python code can't find the `pdftoppm` command.

**Quick check:** After installing, open a NEW terminal and run:
```bash
where pdftoppm
```

It should show: `C:\poppler\Library\bin\pdftoppm.exe`

If not, the PATH wasn't set correctly - try the steps again.

---

**Once installed, your PDF processing will work perfectly!**
