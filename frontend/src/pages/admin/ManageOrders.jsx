import { useEffect, useState } from 'react'
import OrderTable from '../../components/admin/OrderTable'
import { getAdminOrders } from '../../services/orderService'

const ORDER_STATUSES = [
  'pending',
  'confirmed',
  'processing',
  'shipped',
  'delivered',
  'cancelled',
]

function ManageOrders() {
  const [orders, setOrders] = useState([])
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let ignore = false

    async function fetchOrders() {
      try {
        const result = await getAdminOrders(status)

        if (!ignore) {
          setOrders(result)
          setError('')
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || 'Unable to load orders.')
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    fetchOrders()

    return () => {
      ignore = true
    }
  }, [status])

  return (
    <section className="admin-page">
      <div className="admin-page-heading">
        <div>
          <h1>Manage Orders</h1>
          <p>View customer orders and manage their status.</p>
        </div>
      </div>

      <div className="admin-order-filters">
        <label htmlFor="order-status-filter">
          Filter by status
        </label>

        <select
          id="order-status-filter"
          value={status}
          onChange={(event) => setStatus(event.target.value)}
        >
          <option value="">All Orders</option>

          {ORDER_STATUSES.map((orderStatus) => (
            <option key={orderStatus} value={orderStatus}>
              {orderStatus.charAt(0).toUpperCase() +
                orderStatus.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {loading && <p>Loading orders...</p>}

      {error && (
        <p className="admin-error" role="alert">
          {error}
        </p>
      )}

      {!loading && !error && (
        <>
          <p className="admin-order-count">
            {orders.length} {orders.length === 1 ? 'order' : 'orders'} found
          </p>

          <OrderTable orders={orders} />
        </>
      )}
    </section>
  )
}

export default ManageOrders