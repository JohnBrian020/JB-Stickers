
import { apiRequest } from './api'

export async function loginAdmin(identifier, password) {
  const response = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ identifier, password }),
  })

  return response.data
}

export async function getCurrentAdmin() {
  const response = await apiRequest('/auth/me')
  return response.data
}

export async function logoutAdmin() {
  return apiRequest('/auth/logout', {
    method: 'POST',
  })
}
