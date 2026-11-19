import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  getAdminOrderById,
  updateAdminOrderStatus,
} from '../../services/orderService'

const ORDER_STATUSES = [
  'pending',
  'confirmed',
  'processing',
  'shipped',
  'delivered',
  'cancelled',
]

function formatCurrency(amount) {
  return `KSh ${Number(amount).toLocaleString('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function formatDate(date) {
  if (!date) return 'N/A'

  return new Date(date).toLocaleString('en-KE', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

function OrderDetails() {
  const { orderId } = useParams()

  const [order, setOrder] = useState(null)
  const [selectedStatus, setSelectedStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    async function fetchOrder() {
      try {
        const result = await getAdminOrderById(orderId)

        if (!ignore) {
          setOrder(result)
          setSelectedStatus(result.status)
          setError('')
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || 'Unable to load order details.')
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    fetchOrder()

    return () => {
      ignore = true
    }
  }, [orderId])

  async function handleStatusUpdate(event) {
    event.preventDefault()

    if (!order || selectedStatus === order.status) {
      return
    }

    try {
      setSaving(true)
      setError('')
      setMessage('')

      const updatedOrder = await updateAdminOrderStatus(
        order.id,
        selectedStatus
      )

      setOrder(updatedOrder)
      setSelectedStatus(updatedOrder.status)
      setMessage('Order status updated successfully.')
    } catch (err) {
      setError(err.message || 'Unable to update order status.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <p>Loading order details...</p>
  }

  if (!order) {
    return (
      <section className="admin-page">
        <p className="admin-error">
          {error || 'Order not found.'}
        </p>

        <Link to="/admin/orders" className="admin-back-link">
          Back to Orders
        </Link>
      </section>
    )
  }

  return (
    <section className="admin-page">
      <Link to="/admin/orders" className="admin-back-link">
        ← Back to Orders
      </Link>

      <div className="admin-page-heading">
        <div>
          <h1>Order #{order.id}</h1>
          <p>Placed on {formatDate(order.created_at)}</p>
        </div>

        <span className={`order-status status-${order.status}`}>
          {order.status}
        </span>
      </div>

      {error && (
        <p className="admin-error" role="alert">
          {error}
        </p>
      )}

      {message && (
        <p className="admin-success" role="status">
          {message}
        </p>
      )}

      <div className="admin-order-details-grid">
        <div className="admin-order-card">
          <h2>Customer Information</h2>

          <p>
            <strong>Name:</strong> {order.customer.name}
          </p>

          <p>
            <strong>Email:</strong> {order.customer.email}
          </p>

          <p>
            <strong>Phone:</strong> {order.customer.phone}
          </p>

          <p>
            <strong>Address:</strong> {order.customer.address}
          </p>
        </div>

        <div className="admin-order-card">
          <h2>Order Information</h2>

          <p>
            <strong>Order ID:</strong> #{order.id}
          </p>

          <p>
            <strong>Date:</strong> {formatDate(order.created_at)}
          </p>

          <p>
            <strong>Status:</strong> {order.status}
          </p>

          <p>
            <strong>Total:</strong> {formatCurrency(order.total_amount)}
          </p>
        </div>
      </div>

      <div className="admin-order-card admin-order-items">
        <h2>Ordered Products</h2>

        <div className="admin-table-wrapper">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Unit Price</th>
                <th>Quantity</th>
                <th>Subtotal</th>
              </tr>
            </thead>

            <tbody>
              {order.items.map((item) => (
                <tr key={item.id}>
                  <td>{item.product_name}</td>
                  <td>{formatCurrency(item.unit_price)}</td>
                  <td>{item.quantity}</td>
                  <td>{formatCurrency(item.subtotal)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="admin-order-total">
          Total: {formatCurrency(order.total_amount)}
        </div>
      </div>

      <form
        className="admin-order-status-form"
        onSubmit={handleStatusUpdate}
      >
        <h2>Update Order Status</h2>

        <div className="admin-order-status-controls">
          <select
            aria-label="New order status"
            value={selectedStatus}
            onChange={(event) => setSelectedStatus(event.target.value)}
          >
            {ORDER_STATUSES.map((status) => (
              <option key={status} value={status}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </option>
            ))}
          </select>

          <button
            type="submit"
            className="admin-primary-button"
            disabled={saving || selectedStatus === order.status}
          >
            {saving ? 'Updating...' : 'Update Status'}
          </button>
        </div>
      </form>
    </section>
  )
}

export default OrderDetails