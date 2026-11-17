import { apiRequest } from './api'

export async function createOrder(orderData) {
  const response = await apiRequest('/orders', {
    method: 'POST',
    body: JSON.stringify(orderData),
  })

  return response.data
}

export async function getTrackedOrder(trackingToken) {
  const response = await apiRequest(
    `/orders/track/${encodeURIComponent(trackingToken)}`
  )

  return response.data
}