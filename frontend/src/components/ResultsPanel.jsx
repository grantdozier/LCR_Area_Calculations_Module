import React, { useState } from 'react'
import PlanViewer from './PlanViewer'
import Legend from './Legend'
import './ResultsPanel.css'

function ResultsPanel({ results }) {
  const [selectedType, setSelectedType] = useState('all')
  const [selectedSheet, setSelectedSheet] = useState(null)
  const [showReviewOnly, setShowReviewOnly] = useState(false)
  const [highlightedPolygonId, setHighlightedPolygonId] = useState(null)
  const planViewerRef = React.useRef(null)

  const { summary, polygons, filename, sheets_processed, sheets } = results

  // Auto-select first sheet if available
  React.useEffect(() => {
    if (sheets && sheets.length > 0 && !selectedSheet) {
      setSelectedSheet(sheets[0].sheet_number)
    }
  }, [sheets])

  const filteredPolygons = polygons.filter(p => {
    const sheetMatch = selectedSheet === null || p.sheet === selectedSheet
    const typeMatch = selectedType === 'all' || p.type === selectedType
    const reviewMatch = !showReviewOnly || p.review_needed
    return sheetMatch && typeMatch && reviewMatch
  })

  const reviewNeededPolygons = polygons.filter(p => {
    const sheetMatch = selectedSheet === null || p.sheet === selectedSheet
    return sheetMatch && p.review_needed
  })

  const downloadCSV = () => {
    // Generate CSV content
    let csv = 'Polygon ID,Sheet,Surface Type,Area (sqft),Perimeter Type\n'

    polygons.forEach(poly => {
      const perimeterType = ['concrete', 'asphalt', 'building'].includes(poly.type)
        ? 'Impervious'
        : 'Pervious'

      csv += `${poly.id},${poly.sheet},${poly.type},${poly.area_sqft},${perimeterType}\n`
    })

    // Create download link
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename.replace('.pdf', '')}_results.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const currentSheet = sheets?.find(s => s.sheet_number === selectedSheet)

  const handlePolygonCardClick = (poly) => {
    // Switch to the polygon's sheet if not already there
    if (selectedSheet !== poly.sheet) {
      setSelectedSheet(poly.sheet)
    }
    // Highlight the polygon
    setHighlightedPolygonId(poly.id)
    // Scroll to the plan viewer
    if (planViewerRef.current) {
      planViewerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  return (
    <div className="results-panel">
      {/* Header Section */}
      <div className="results-header">
        <h2>Processing Results</h2>
        <button className="download-button" onClick={downloadCSV}>
          ⬇ Download CSV
        </button>
      </div>

      {/* File Info */}
      <div className="results-info">
        <p><strong>File:</strong> {filename}</p>
        <p><strong>Sheets Processed:</strong> {sheets_processed}</p>
        <p><strong>Total Polygons:</strong> {summary.total_polygons}</p>
        {summary.polygons_needing_review > 0 && (
          <p className="review-warning-text">
            <strong>⚠ {summary.polygons_needing_review} polygon(s) need review</strong>
          </p>
        )}
      </div>

      {/* Main Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card impervious">
          <h3>Total Impervious</h3>
          <p className="area-value">{summary.total_impervious_sqft.toLocaleString()}</p>
          <p className="area-unit">square feet</p>
          <p className="percentage">{summary.percent_impervious}%</p>
        </div>

        <div className="summary-card pervious">
          <h3>Total Pervious</h3>
          <p className="area-value">{summary.total_pervious_sqft.toLocaleString()}</p>
          <p className="area-unit">square feet</p>
          <p className="percentage">{summary.percent_pervious}%</p>
        </div>

        <div className="summary-card total">
          <h3>Total Site Area</h3>
          <p className="area-value">{summary.total_site_area_sqft.toLocaleString()}</p>
          <p className="area-unit">square feet</p>
        </div>
      </div>

      {/* DIA-Format Organized Breakdown */}
      <div className="categorized-breakdown">
        <h3>Surface Area Summary (DIA Format)</h3>

        <div className="category-section">
          <h4 className="category-title impervious-title">Impervious Surfaces</h4>
          <div className="category-items">
            <div className="category-item">
              <span className="item-label">Building Footprints</span>
              <span className="item-value">
                {summary.categorized.impervious_surfaces.building_footprints.toLocaleString()} sqft
              </span>
            </div>
            <div className="category-item">
              <span className="item-label">Concrete Paving</span>
              <span className="item-value">
                {summary.categorized.impervious_surfaces.concrete_paving.toLocaleString()} sqft
              </span>
            </div>
            <div className="category-item">
              <span className="item-label">Asphalt Paving</span>
              <span className="item-value">
                {summary.categorized.impervious_surfaces.asphalt_paving.toLocaleString()} sqft
              </span>
            </div>
            <div className="category-item subtotal">
              <span className="item-label">Impervious Subtotal</span>
              <span className="item-value">
                {summary.categorized.impervious_surfaces.subtotal.toLocaleString()} sqft
              </span>
            </div>
          </div>
        </div>

        <div className="category-section">
          <h4 className="category-title pervious-title">Pervious Surfaces</h4>
          <div className="category-items">
            <div className="category-item">
              <span className="item-label">Turf / Grass</span>
              <span className="item-value">
                {summary.categorized.pervious_surfaces.turf_grass.toLocaleString()} sqft
              </span>
            </div>
            <div className="category-item subtotal">
              <span className="item-label">Pervious Subtotal</span>
              <span className="item-value">
                {summary.categorized.pervious_surfaces.subtotal.toLocaleString()} sqft
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <Legend />

      {/* Sheet Navigation */}
      {sheets && sheets.length > 0 && (
        <div className="sheet-navigation">
          <h3>Sheet-by-Sheet View</h3>
          <div className="sheet-tabs">
            {sheets.map((sheet) => (
              <button
                key={sheet.sheet_number}
                className={`sheet-tab ${selectedSheet === sheet.sheet_number ? 'active' : ''}`}
                onClick={() => {
                  setSelectedSheet(sheet.sheet_number)
                  setHighlightedPolygonId(null)  // Clear highlight when switching sheets
                }}
              >
                Sheet {sheet.sheet_number}
                <span className="tab-count">({sheet.polygons_count})</span>
              </button>
            ))}
          </div>

          {/* Sheet Summary Stats */}
          {currentSheet && (
            <div className="sheet-summary">
              <div className="sheet-summary-card">
                <span className="summary-label">Impervious</span>
                <span className="summary-value">
                  {currentSheet.sheet_totals.impervious.toLocaleString()} sqft
                </span>
              </div>
              <div className="sheet-summary-card">
                <span className="summary-label">Pervious</span>
                <span className="summary-value">
                  {currentSheet.sheet_totals.pervious.toLocaleString()} sqft
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Plan Viewer */}
      {currentSheet && (
        <div ref={planViewerRef}>
          <PlanViewer 
            sheet={currentSheet} 
            highlightedPolygonId={highlightedPolygonId}
            onPolygonSelect={(id) => setHighlightedPolygonId(id)}
          />
        </div>
      )}

      {/* Polygons List Section */}
      <div className="polygons-section">
        <div className="polygons-header">
          <h3>All Detected Polygons ({filteredPolygons.length})</h3>
          <div className="filters">
            <select
              className="filter-select"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="concrete">Concrete</option>
              <option value="asphalt">Asphalt</option>
              <option value="building">Building</option>
              <option value="pervious">Pervious</option>
            </select>

            {reviewNeededPolygons.length > 0 && (
              <label className="review-filter">
                <input
                  type="checkbox"
                  checked={showReviewOnly}
                  onChange={(e) => setShowReviewOnly(e.target.checked)}
                />
                Show Review Needed Only ({reviewNeededPolygons.length})
              </label>
            )}
          </div>
        </div>

        <div className="polygons-list">
          {filteredPolygons.map((poly) => (
            <div 
              key={poly.id} 
              className={`polygon-card ${poly.type} ${poly.review_needed ? 'needs-review' : ''} ${highlightedPolygonId === poly.id ? 'highlighted' : ''}`}
              onClick={() => handlePolygonCardClick(poly)}
              style={{ cursor: 'pointer' }}
            >
              <div className="polygon-header">
                <span className="polygon-id">{poly.id}</span>
                <span className={`polygon-type-badge ${poly.type}`}>
                  {poly.type}
                </span>
                {poly.review_needed && (
                  <span className="review-badge">⚠ Review</span>
                )}
              </div>
              <div className="polygon-details">
                <div className="detail-item">
                  <span className="detail-label">Sheet:</span>
                  <span className="detail-value">{poly.sheet}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Area:</span>
                  <span className="detail-value">{poly.area_sqft.toLocaleString()} sqft</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Confidence:</span>
                  <span className="detail-value">{(poly.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
              {poly.review_needed && poly.review_reasons && (
                <div className="review-reasons">
                  <strong>Reasons:</strong>
                  <ul>
                    {poly.review_reasons.map((reason, idx) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ResultsPanel
