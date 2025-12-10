import React, { useRef, useEffect, useState } from 'react'
import './PlanViewer.css'

const SURFACE_COLORS = {
  building: { fill: 'rgba(200, 0, 0, 0.4)', stroke: 'rgb(200, 0, 0)', label: 'Bldg' },
  concrete: { fill: 'rgba(128, 128, 128, 0.4)', stroke: 'rgb(128, 128, 128)', label: 'Conc' },
  asphalt: { fill: 'rgba(50, 50, 50, 0.4)', stroke: 'rgb(50, 50, 50)', label: 'Asph' },
  pervious: { fill: 'rgba(0, 200, 0, 0.3)', stroke: 'rgb(0, 200, 0)', label: 'Perv' },
  water: { fill: 'rgba(0, 100, 200, 0.4)', stroke: 'rgb(0, 100, 200)', label: 'Water' }
}

function PlanViewer({ sheet, highlightedPolygonId, onPolygonSelect }) {
  const canvasRef = useRef(null)
  const [selectedPolygon, setSelectedPolygon] = useState(null)
  const [hoveredPolygon, setHoveredPolygon] = useState(null)
  const [imageLoaded, setImageLoaded] = useState(false)
  const [viewDimensions, setViewDimensions] = useState({ width: 0, height: 0 })
  const imageRef = useRef(null)

  // PDF coordinate system info from backend
  const pdfWidth = sheet.pdf_width || 612   // Default letter size
  const pdfHeight = sheet.pdf_height || 792

  // Load new image when sheet changes
  useEffect(() => {
    if (!sheet || !sheet.image_base64) return

    // Reset state for new sheet
    setImageLoaded(false)
    setSelectedPolygon(null)
    setHoveredPolygon(null)

    const img = new Image()
    img.onload = () => {
      imageRef.current = img
      setImageLoaded(true)
    }
    img.src = sheet.image_base64
  }, [sheet.sheet_number, sheet.image_base64])  // Depend on sheet number and image

  // Sync external highlight with internal selection
  useEffect(() => {
    if (highlightedPolygonId) {
      setSelectedPolygon(highlightedPolygonId)
    }
  }, [highlightedPolygonId])

  // Redraw canvas when state changes
  useEffect(() => {
    if (imageLoaded && imageRef.current) {
      drawCanvas()
    }
  }, [imageLoaded, hoveredPolygon, selectedPolygon, highlightedPolygonId, pdfWidth, pdfHeight])

  // Transform PDF coordinates to screen coordinates
  const mapPdfToScreen = (pdfX, pdfY, vw = viewDimensions.width, vh = viewDimensions.height) => {
    if (vw === 0 || vh === 0) return { x: 0, y: 0 }
    
    const scaleX = vw / pdfWidth
    const scaleY = vh / pdfHeight
    
    return {
      x: pdfX * scaleX,
      // PDF origin is bottom-left, screen origin is top-left, so flip Y
      y: (pdfHeight - pdfY) * scaleY
    }
  }

  // Transform screen coordinates back to PDF coordinates (for hit testing)
  const mapScreenToPdf = (screenX, screenY) => {
    if (viewDimensions.width === 0 || viewDimensions.height === 0) return { x: 0, y: 0 }
    
    const scaleX = viewDimensions.width / pdfWidth
    const scaleY = viewDimensions.height / pdfHeight
    
    return {
      x: screenX / scaleX,
      y: pdfHeight - (screenY / scaleY)
    }
  }

  const drawCanvas = () => {
    const canvas = canvasRef.current
    const img = imageRef.current
    if (!canvas || !img) return

    const ctx = canvas.getContext('2d')
    const maxWidth = canvas.parentElement.clientWidth - 40
    const displayScale = maxWidth / img.width

    const viewWidth = img.width * displayScale
    const viewHeight = img.height * displayScale
    
    canvas.width = viewWidth
    canvas.height = viewHeight
    setViewDimensions({ width: viewWidth, height: viewHeight })

    // Draw base image
    ctx.drawImage(img, 0, 0, viewWidth, viewHeight)

    // Local transform function using current dimensions (not stale state)
    const toScreen = (pdfX, pdfY) => {
      const scaleX = viewWidth / pdfWidth
      const scaleY = viewHeight / pdfHeight
      return {
        x: pdfX * scaleX,
        y: (pdfHeight - pdfY) * scaleY
      }
    }

    // Draw polygons using PDF coordinate transformation
    sheet.polygons.forEach((polygon) => {
      const isHovered = hoveredPolygon === polygon.id
      const isSelected = selectedPolygon === polygon.id
      const isHighlighted = highlightedPolygonId === polygon.id
      const colors = SURFACE_COLORS[polygon.type] || SURFACE_COLORS.pervious

      // Get coordinates - support both old format (coordinates) and new format (coords_pdf)
      const coords = polygon.coords_pdf || polygon.coordinates
      if (!coords || coords.length < 3) return

      ctx.save()

      // Draw filled polygon using transformed coordinates
      ctx.beginPath()
      coords.forEach((coord, idx) => {
        const screenPt = toScreen(coord[0], coord[1])
        if (idx === 0) {
          ctx.moveTo(screenPt.x, screenPt.y)
        } else {
          ctx.lineTo(screenPt.x, screenPt.y)
        }
      })
      ctx.closePath()

      // Apply fill
      ctx.fillStyle = isHovered || isSelected || isHighlighted
        ? colors.fill.replace('0.4', '0.7').replace('0.3', '0.6')
        : colors.fill
      ctx.fill()

      // Apply stroke
      ctx.strokeStyle = isHighlighted ? 'rgb(255, 165, 0)' : colors.stroke
      ctx.lineWidth = isHighlighted ? 4 : isSelected ? 3 : isHovered ? 2 : 1
      ctx.stroke()

      // Draw label at centroid
      const centroidSum = coords.reduce((acc, coord) => {
        const pt = toScreen(coord[0], coord[1])
        return { x: acc.x + pt.x, y: acc.y + pt.y }
      }, { x: 0, y: 0 })
      const centroid = { x: centroidSum.x / coords.length, y: centroidSum.y / coords.length }
      
      ctx.font = 'bold 10px Arial'
      ctx.fillStyle = 'white'
      ctx.strokeStyle = 'black'
      ctx.lineWidth = 2
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      ctx.strokeText(colors.label, centroid.x, centroid.y)
      ctx.fillText(colors.label, centroid.x, centroid.y)

      ctx.restore()
    })
  }

  const handleCanvasClick = (event) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const screenX = event.clientX - rect.left
    const screenY = event.clientY - rect.top
    const pdfPt = mapScreenToPdf(screenX, screenY)

    // Check if click is inside any polygon (in PDF coordinate space)
    for (const polygon of sheet.polygons) {
      const coords = polygon.coords_pdf || polygon.coordinates
      if (coords && isPointInPolygonPdf(pdfPt.x, pdfPt.y, coords)) {
        const newSelection = selectedPolygon === polygon.id ? null : polygon.id
        setSelectedPolygon(newSelection)
        if (onPolygonSelect) {
          onPolygonSelect(newSelection)
        }
        return
      }
    }

    setSelectedPolygon(null)
  }

  const handleCanvasMouseMove = (event) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const screenX = event.clientX - rect.left
    const screenY = event.clientY - rect.top
    const pdfPt = mapScreenToPdf(screenX, screenY)

    // Check if mouse is over any polygon (in PDF coordinate space)
    for (const polygon of sheet.polygons) {
      const coords = polygon.coords_pdf || polygon.coordinates
      if (coords && isPointInPolygonPdf(pdfPt.x, pdfPt.y, coords)) {
        if (hoveredPolygon !== polygon.id) {
          setHoveredPolygon(polygon.id)
          canvas.style.cursor = 'pointer'
        }
        return
      }
    }

    if (hoveredPolygon !== null) {
      setHoveredPolygon(null)
      canvas.style.cursor = 'default'
    }
  }

  // Point-in-polygon test using PDF coordinates
  const isPointInPolygonPdf = (x, y, coordsPdf) => {
    let inside = false
    for (let i = 0, j = coordsPdf.length - 1; i < coordsPdf.length; j = i++) {
      const xi = coordsPdf[i][0], yi = coordsPdf[i][1]
      const xj = coordsPdf[j][0], yj = coordsPdf[j][1]

      const intersect = ((yi > y) !== (yj > y)) &&
        (x < (xj - xi) * (y - yi) / (yj - yi) + xi)
      if (intersect) inside = !inside
    }
    return inside
  }

  const getSelectedPolygonData = () => {
    if (!selectedPolygon) return null
    return sheet.polygons.find(p => p.id === selectedPolygon)
  }

  const selectedData = getSelectedPolygonData()

  return (
    <div className="plan-viewer">
      <div className="plan-viewer-header">
        <h3>Sheet {sheet.sheet_number} - Visual Overlay</h3>
        <div className="sheet-stats">
          <span>{sheet.polygons_count} polygons</span>
          <span className="separator">•</span>
          <span>PDF: {pdfWidth.toFixed(0)} × {pdfHeight.toFixed(0)}</span>
        </div>
      </div>

      <div className="canvas-container">
        <canvas
          ref={canvasRef}
          onClick={handleCanvasClick}
          onMouseMove={handleCanvasMouseMove}
          onMouseLeave={() => setHoveredPolygon(null)}
        />
      </div>

      {selectedData && (
        <div className="polygon-details-card">
          <div className="details-header">
            <h4>{selectedData.id}</h4>
            <span className={`type-badge ${selectedData.type}`}>
              {selectedData.type}
            </span>
          </div>
          <div className="details-body">
            <div className="detail-row">
              <span className="label">Area:</span>
              <span className="value">{selectedData.area_sqft.toLocaleString()} sqft</span>
            </div>
            <div className="detail-row">
              <span className="label">Confidence:</span>
              <span className="value">{(selectedData.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="detail-row">
              <span className="label">Source:</span>
              <span className="value">{selectedData.source || 'vector'}</span>
            </div>
            {selectedData.review_needed && (
              <div className="review-warning">
                <strong>⚠ Review Needed</strong>
                <ul>
                  {selectedData.review_reasons.map((reason, idx) => (
                    <li key={idx}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          <button
            className="close-details-btn"
            onClick={() => setSelectedPolygon(null)}
          >
            Close
          </button>
        </div>
      )}
    </div>
  )
}

export default PlanViewer
