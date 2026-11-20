
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

// Keep the CSRF token in memory, not localStorage.
let csrfToken = null
let csrfTokenPromise = null

async function getCsrfToken() {
  if (csrfToken) {
    return csrfToken
  }

  // Avoid duplicate token requests when several API calls start together.
  if (!csrfTokenPromise) {
    csrfTokenPromise = (async () => {
      const response = await fetch(`${API_BASE_URL}/auth/csrf-token`, {
        method: 'GET',
        credentials: 'include',
      })

      const result = await response.json()

      if (!response.ok || !result.data?.csrf_token) {
        throw new Error(
          result.message || 'Could not obtain security token'
        )
      }

      csrfToken = result.data.csrf_token
      return csrfToken
    })()
  }

  try {
    return await csrfTokenPromise
  } finally {
    csrfTokenPromise = null
  }
}

export async function apiRequest(endpoint, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const isFormData = options.body instanceof FormData
  const headers = { ...options.headers }

  const requiresCsrf = !['GET', 'HEAD', 'OPTIONS'].includes(method)

  if (requiresCsrf) {
    headers['X-CSRFToken'] = await getCsrfToken()
  }

  // FormData must set its own multipart Content-Type boundary.
  if (!isFormData && options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    method,
    headers,
    credentials: 'include',
  })

  const result = await response.json()

    if (!response.ok) {
    if (
      response.status === 403 &&
      result.message?.toLowerCase().includes('csrf')
    ) {
      csrfToken = null
    }

    throw new Error(result.message || 'Something went wrong')
  }

  // Login and logout rotate the CSRF token.
  if (result.data?.csrf_token) {
    csrfToken = result.data.csrf_token
  }

  return result
}
