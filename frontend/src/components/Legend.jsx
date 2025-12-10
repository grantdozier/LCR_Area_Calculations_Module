import React from 'react'
import './Legend.css'

const LEGEND_ITEMS = [
  { type: 'building', color: 'rgb(200, 0, 0)', label: 'Building Footprint', shortLabel: 'Bldg' },
  { type: 'concrete', color: 'rgb(128, 128, 128)', label: 'Concrete Paving', shortLabel: 'Conc' },
  { type: 'asphalt', color: 'rgb(50, 50, 50)', label: 'Asphalt Paving', shortLabel: 'Asph' },
  { type: 'pervious', color: 'rgb(0, 200, 0)', label: 'Pervious Surface', shortLabel: 'Perv' }
]

function Legend() {
  return (
    <div className="legend">
      <h4>Legend</h4>
      <div className="legend-items">
        {LEGEND_ITEMS.map((item) => (
          <div key={item.type} className="legend-item">
            <div
              className="legend-color-box"
              style={{
                backgroundColor: item.color.replace('rgb', 'rgba').replace(')', ', 0.4)'),
                border: `2px solid ${item.color}`
              }}
            >
              <span className="legend-short-label">{item.shortLabel}</span>
            </div>
            <span className="legend-label">{item.label}</span>
          </div>
        ))}
      </div>
      <div className="legend-symbols">
        <div className="legend-symbol">
          <span className="symbol">⚠</span>
          <span className="symbol-label">Needs Review</span>
        </div>
      </div>
    </div>
  )
}

export default Legend
