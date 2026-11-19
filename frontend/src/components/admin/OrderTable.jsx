import { Link } from 'react-router-dom'

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

function OrderTable({ orders }) {
  if (orders.length === 0) {
    return <p className="admin-empty">No orders found.</p>
  }

  return (
    <div className="admin-table-wrapper">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Customer</th>
            <th>Date</th>
            <th>Items</th>
            <th>Total</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {orders.map((order) => (
            <tr key={order.id}>
              <td>#{order.id}</td>

              <td>
                <strong>{order.customer?.name || 'Unknown'}</strong>
                <br />
                <small>{order.customer?.email || 'No email'}</small>
              </td>

              <td>{formatDate(order.created_at)}</td>

              <td>
                {order.items.reduce(
                  (total, item) => total + item.quantity,
                  0
                )}
              </td>

              <td>{formatCurrency(order.total_amount)}</td>

              <td>
                <span
                  className={`order-status status-${order.status}`}
                >
                  {order.status}
                </span>
              </td>

              <td>
                <Link
                  to={`/admin/orders/${order.id}`}
                  className="admin-action-button"
                >
                  View Details
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default OrderTable