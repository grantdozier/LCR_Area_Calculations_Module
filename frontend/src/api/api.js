import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export async function processPDF(file) {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await axios.post(`${API_BASE_URL}/api/process`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      // Increase timeout to handle large, multi-page PDFs without client-side aborts
      timeout: 600000 // 10 minute timeout
    })

    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Server error')
    } else if (error.request) {
      throw new Error('No response from server. Is the backend running?')
    } else {
      throw new Error('Failed to upload file')
    }
  }
}

export async function startProcessJob(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post(`${API_BASE_URL}/api/process/start`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  return response.data
}

export async function getProcessStatus(jobId) {
  const response = await axios.get(`${API_BASE_URL}/api/process/status/${jobId}`)
  return response.data
}

export async function healthCheck() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/health`)
    return response.data
  } catch (error) {
    return { status: 'offline' }
  }
}
