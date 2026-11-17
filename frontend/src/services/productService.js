import { apiRequest } from './api'

export async function getProducts() {
  const response = await apiRequest('/products')
  return response.data
}

export async function getProductById(productId) {
  const response = await apiRequest(`/products/${productId}`)
  return response.data
}

// Admin functions
export async function getAdminProducts() {
  const response = await apiRequest('/products/admin')
  return response.data
}

export async function createProduct(productData) {
  const response = await apiRequest('/products', {
    method: 'POST',
    body: JSON.stringify(productData),
  })

  return response.data
}

export async function updateProduct(productId, productData) {
  const response = await apiRequest(`/products/${productId}`, {
    method: 'PATCH',
    body: JSON.stringify(productData),
  })

  return response.data
}

export async function deleteProduct(productId) {
  return apiRequest(`/products/${productId}`, {
    method: 'DELETE',
  })
}