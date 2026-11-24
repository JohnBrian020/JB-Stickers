import { apiRequest } from './api'

export async function createOrder(orderData) {
  const response = await apiRequest('/orders', {
    method: 'POST',
    body: JSON.stringify(orderData),
  })

  return response.data
}

export async function initiateMpesaPayment(orderData) {
  const response = await apiRequest('/payments/stk-push', {
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

// Admin: retrieve all orders, optionally filtered by status.
export async function getAdminOrders(status = '') {
  const query = status
    ? `?status=${encodeURIComponent(status)}`
    : ''

  const response = await apiRequest(`/admin/orders${query}`)

  return response.data
}

// Admin: retrieve one order.
export async function getAdminOrderById(orderId) {
  const response = await apiRequest(`/admin/orders/${orderId}`)

  return response.data
}

// Admin: update an order's status.
export async function updateAdminOrderStatus(orderId, status) {
  const response = await apiRequest(`/admin/orders/${orderId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })

  return response.data
}