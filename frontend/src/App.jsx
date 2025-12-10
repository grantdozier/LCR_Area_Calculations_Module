import React, { useState, useEffect, useRef } from 'react'
import FileUpload from './components/FileUpload'
import ResultsPanel from './components/ResultsPanel'
import { startProcessJob, getProcessStatus } from './api/api'
import './App.css'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState({ currentSheet: 0, totalSheets: 0, status: 'idle' })
  const pollIntervalRef = useRef(null)

  const handleFileUpload = async (file) => {
    setLoading(true)
    setError(null)
    setResults(null)
    setProgress({ currentSheet: 0, totalSheets: 0, status: 'starting' })

    try {
      const { job_id: jobId } = await startProcessJob(file)

      setProgress((prev) => ({ ...prev, status: 'running' }))

      const poll = async () => {
        try {
          const status = await getProcessStatus(jobId)

          setProgress({
            currentSheet: status.current_sheet || 0,
            totalSheets: status.total_sheets || 0,
            status: status.status || 'unknown'
          })

          if (status.status === 'completed') {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current)
              pollIntervalRef.current = null
            }
            if (status.result) {
              setResults(status.result)
            }
            setLoading(false)
          } else if (status.status === 'error') {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current)
              pollIntervalRef.current = null
            }
            setError(status.error || 'Processing failed')
            setLoading(false)
          }
        } catch (err) {
          console.error('Status polling error:', err)
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current)
            pollIntervalRef.current = null
          }
          setError('Lost connection to processing job')
          setLoading(false)
        }
      }

      pollIntervalRef.current = setInterval(poll, 3000)
      // Fire first poll immediately
      poll()
    } catch (err) {
      setError(err.message || 'Failed to start processing job')
      console.error('Upload error:', err)
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>LCR Area Calculations</h1>
        <p>Module A - PDF-based Area Extraction</p>
      </header>

      <main className="app-main">
        <div className="upload-section">
          <FileUpload onUpload={handleFileUpload} loading={loading} />

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Processing PDF... This may take a while for large plan sets.</p>
              {progress.totalSheets > 0 && (
                <p>
                  Sheet {progress.currentSheet} of {progress.totalSheets}
                </p>
              )}
            </div>
          )}

          {error && (
            <div className="error">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        {results && !loading && (
          <ResultsPanel results={results} />
        )}
      </main>

      <footer className="app-footer">
        <p>Module A v1.0.0 | PDF Processing Engine</p>
      </footer>
    </div>
  )
}

export default App
