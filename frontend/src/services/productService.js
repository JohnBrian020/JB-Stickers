import { apiRequest } from './api'

export async function getProducts() {
  const response = await apiRequest('/products')

  return response.data
}

export async function getProductById(productId) {
  const response = await apiRequest(`/products/${productId}`)

  return response.data
}