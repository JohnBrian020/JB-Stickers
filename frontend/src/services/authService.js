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

export async function updateAdminProfile(profileData) {
  const response = await apiRequest('/auth/profile', {
    method: 'PATCH',
    body: JSON.stringify(profileData),
  })

  return response.data
}

export async function updateAdminPassword(passwordData) {
  return apiRequest('/auth/password', {
    method: 'PATCH',
    body: JSON.stringify(passwordData),
  })
}
