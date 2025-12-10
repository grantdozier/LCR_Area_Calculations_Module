# Phase 1 Testing Guide

## Pre-Testing Checklist

### Backend Requirements
- [ ] Python 3.9+ installed
- [ ] Virtual environment activated (`backend/venv`)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Poppler installed for PDF processing
- [ ] Tesseract OCR installed

### Frontend Requirements
- [ ] Node.js 16+ installed
- [ ] Dependencies installed (`npm install` in frontend directory)

---

## Step-by-Step Testing Instructions

### Step 1: Start the Backend Server

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start the server
python main.py
```

**Expected Output:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Verify Backend is Running:**
- Open browser to http://localhost:8000
- You should see: `{"status":"online","module":"Module A - PDF Area Extraction","version":"1.0.0"}`

---

### Step 2: Start the Frontend Development Server

Open a **second terminal**:

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
VITE vX.X.X  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Verify Frontend is Running:**
- Open browser to http://localhost:5173 (or the port shown)
- You should see the LCR Area Calculations interface

---

### Step 3: Upload and Process a PDF

1. **Prepare a Test PDF:**
   - Use a civil engineering plan set (recommended: from `Resources/` folder)
   - Or use any PDF with drawings containing polygons

2. **Upload the PDF:**
   - Click the upload area or drag and drop the PDF
   - Wait for processing to complete
   - Processing time depends on:
     - Number of pages (sheets)
     - Complexity of drawings
     - System performance

3. **Monitor Progress:**
   - Watch the progress indicator
   - Should show "Sheet X of Y"
   - Backend console will show detailed processing logs

---

## Feature Testing Checklist

### ✅ Test 1: Enhanced Summary Statistics

**What to Check:**
- [ ] "Total Impervious" card shows value and percentage
- [ ] "Total Pervious" card shows value and percentage
- [ ] "Total Site Area" card displays correctly
- [ ] All numbers are formatted with commas (e.g., 12,500.5)
- [ ] Percentages add up to 100%

**Screenshot Location:** Top section of results

---

### ✅ Test 2: DIA-Format Organized Breakdown

**What to Check:**
- [ ] Section titled "Surface Area Summary (DIA Format)" exists
- [ ] **Impervious Surfaces** section shows:
  - [ ] Building Footprints with area
  - [ ] Concrete Paving with area
  - [ ] Asphalt Paving with area
  - [ ] Impervious Subtotal (should match Total Impervious card)
- [ ] **Pervious Surfaces** section shows:
  - [ ] Turf/Grass with area
  - [ ] Pervious Subtotal (should match Total Pervious card)
- [ ] Subtotals are highlighted/bold

**Expected Behavior:** Format matches typical DIA reports used in civil engineering

---

### ✅ Test 3: Legend Component

**What to Check:**
- [ ] Legend appears above the sheet navigation
- [ ] Shows 4 surface types with colors:
  - [ ] Building (Red)
  - [ ] Concrete (Gray)
  - [ ] Asphalt (Dark Gray)
  - [ ] Pervious (Green)
- [ ] Each shows abbreviated label (Bldg, Conc, Asph, Perv)
- [ ] Shows ⚠ symbol with "Needs Review" label

---

### ✅ Test 4: Sheet-by-Sheet Navigation

**What to Check:**
- [ ] "Sheet-by-Sheet View" section exists
- [ ] Sheet tabs are present (Sheet 1, Sheet 2, etc.)
- [ ] Tab shows polygon count in parentheses
- [ ] Clicking a tab:
  - [ ] Highlights the selected tab
  - [ ] Shows sheet summary (Impervious/Pervious totals)
  - [ ] Loads the visual overlay below

**Test Multiple Sheets:**
- [ ] Switch between sheets - overlay updates correctly
- [ ] Each sheet shows different polygon counts
- [ ] Sheet totals are different for each sheet

---

### ✅ Test 5: Plan-View Visual Overlay

**What to Check:**
- [ ] Sheet image displays correctly
- [ ] Colored polygons overlay the image
- [ ] Colors match legend:
  - [ ] Red for buildings
  - [ ] Gray for concrete
  - [ ] Dark gray for asphalt
  - [ ] Green for pervious
- [ ] Polygons have semi-transparent fill
- [ ] Polygon borders are visible

**Test Interactions:**
- [ ] **Hover:** Mouse over a polygon → it highlights (darker shade)
- [ ] **Cursor:** Cursor changes to pointer when over a polygon
- [ ] **Click:** Clicking a polygon opens a detail card
- [ ] **Click Outside:** Clicking outside polygons closes the detail card

---

### ✅ Test 6: Surface-Type Labels on Polygons

**What to Check:**
- [ ] Each polygon displays its abbreviated label:
  - [ ] "Bldg" for buildings
  - [ ] "Conc" for concrete
  - [ ] "Asph" for asphalt
  - [ ] "Perv" for pervious
- [ ] Labels are centered on polygons
- [ ] Labels have white text with black outline (readable)
- [ ] Labels are visible on both light and dark backgrounds

---

### ✅ Test 7: Review Needed Flags

**What to Check:**

**In Results Info Section:**
- [ ] If any polygons need review, shows warning:
  - `⚠ X polygon(s) need review`

**In Visual Overlay:**
- [ ] Polygons needing review show ⚠ symbol (red)
- [ ] Symbol appears near the polygon's centroid

**In Polygon Detail Card (when clicked):**
- [ ] "Review Needed" section appears in yellow/orange
- [ ] Lists specific reasons:
  - [ ] "Very small area"
  - [ ] "Very large area"
  - [ ] "Irregular shape"
  - [ ] "Complex polygon"
  - [ ] "Statistical outlier"

**In Polygon List:**
- [ ] Cards needing review have yellow/orange background
- [ ] Shows "⚠ Review" badge
- [ ] "Reasons:" section lists why review is needed

**Review Filter:**
- [ ] Checkbox appears: "Show Review Needed Only (X)"
- [ ] Checking it filters to only show flagged polygons
- [ ] Count matches the summary warning

---

### ✅ Test 8: Polygon Detail Card (Click Interaction)

**What to Check:**
- [ ] Card appears centered on screen
- [ ] Semi-transparent overlay behind card
- [ ] Shows:
  - [ ] Polygon ID
  - [ ] Surface type badge (colored)
  - [ ] Area in square feet
  - [ ] Confidence score (percentage)
  - [ ] Review warning (if applicable)
- [ ] "Close" button dismisses the card
- [ ] Clicking another polygon switches to that polygon's details

---

### ✅ Test 9: Polygon List Filters

**What to Check:**
- [ ] "All Detected Polygons (X)" section exists
- [ ] Dropdown filter shows:
  - [ ] All Types
  - [ ] Concrete
  - [ ] Asphalt
  - [ ] Building
  - [ ] Pervious
- [ ] Selecting a type filters the list correctly
- [ ] Polygon count updates dynamically
- [ ] Filter persists when scrolling

---

### ✅ Test 10: Confidence Scores

**What to Check:**
- [ ] Each polygon card shows "Confidence: X%"
- [ ] Confidence values are between 0% and 100%
- [ ] Most polygons should have confidence > 60%
- [ ] Complex/irregular shapes may have lower confidence
- [ ] Confidence visible in detail card when polygon is clicked

---

## Edge Case Testing

### Test with Small PDF (1-2 pages)
- [ ] Processing completes quickly (< 30 seconds)
- [ ] All features work correctly
- [ ] Sheet navigation shows correct number of sheets

### Test with Large PDF (5+ pages)
- [ ] Progress indicator updates correctly
- [ ] Processing doesn't timeout
- [ ] All sheets are processed
- [ ] Canvas performance is acceptable

### Test with Complex Sheet (Many Polygons)
- [ ] Visual overlay renders all polygons
- [ ] Hover/click interactions remain responsive
- [ ] Labels don't overlap excessively

### Test with Simple Sheet (Few Polygons)
- [ ] All polygons are detected
- [ ] Review flags work correctly
- [ ] Statistics calculate properly

---

## Common Issues and Solutions

### Issue: Canvas Not Displaying
**Solution:**
- Check browser console for errors
- Verify `sheet.image_base64` is present in API response
- Try a different browser (Chrome/Edge recommended)

### Issue: Polygons Not Colored Correctly
**Solution:**
- Check that polygon `type` field is one of: building, concrete, asphalt, pervious
- Verify SURFACE_COLORS mapping in PlanViewer.jsx

### Issue: No Review Flags Appearing
**Solution:**
- Check if polygons meet review criteria (see analyzer.py)
- Verify at least 10 polygons exist for outlier detection
- Look for polygons < 100 sqft or > 50,000 sqft

### Issue: Sheet Tabs Not Switching
**Solution:**
- Check React state in browser dev tools
- Verify `selectedSheet` state updates
- Ensure `sheets` array is populated in results

### Issue: Hover Not Working
**Solution:**
- Check that `isPointInPolygon` function is working
- Verify canvas scale calculation
- Test in different browsers

---

## Performance Benchmarks

### Expected Processing Times
| Plan Set Size | Expected Time |
|---------------|---------------|
| 1-3 pages     | 10-30 seconds |
| 4-8 pages     | 30-60 seconds |
| 9-15 pages    | 1-2 minutes   |

### Expected Accuracy
| Metric                   | Expected Rate |
|--------------------------|---------------|
| Polygon Detection        | ~85%          |
| Surface Classification   | ~70-80%       |
| Review Flag Accuracy     | ~90%          |

---

## Reporting Issues

If you encounter issues, please document:

1. **Steps to Reproduce:** Exact actions taken
2. **Expected Behavior:** What should happen
3. **Actual Behavior:** What actually happened
4. **Screenshots:** Visual evidence of the issue
5. **Console Logs:** Any errors in browser console or backend logs
6. **Environment:**
   - OS (Windows/macOS/Linux)
   - Browser and version
   - Python version
   - Node.js version

---

## Success Criteria

Phase 1 is considered successfully implemented when:

- [x] All 10 feature tests pass
- [x] No console errors during normal operation
- [x] Processing completes for test PDFs
- [x] Visual overlay is interactive and responsive
- [x] Review flags appear and are accurate
- [x] DIA-format breakdown matches expected structure
- [x] Sheet navigation works smoothly

---

**Testing Status:** Ready for Testing
**Last Updated:** 2025-12-10
