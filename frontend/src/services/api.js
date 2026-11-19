const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export async function apiRequest(endpoint, options = {}) {
  const isFormData = options.body instanceof FormData
  const headers = { ...options.headers }

  // FormData must set its own multipart Content-Type boundary.
  if (!isFormData && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include',
  })

  const result = await response.json()

  if (!response.ok) {
    throw new Error(result.message || 'Something went wrong')
  }

  return result
}