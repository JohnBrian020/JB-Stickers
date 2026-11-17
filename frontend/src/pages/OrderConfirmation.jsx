
import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { getTrackedOrder } from '../services/orderService'

function OrderConfirmation() {
  const { trackingToken } = useParams()
  const location = useLocation()

  const [order, setOrder] = useState(location.state?.order || null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(!location.state?.order)

  useEffect(() => {
    if (location.state?.order) return

    async function loadOrder() {
      try {
        const orderData = await getTrackedOrder(trackingToken)
        setOrder(orderData)
      } catch (requestError) {
        setError(requestError.message || 'Could not retrieve your order.')
      } finally {
        setLoading(false)
      }
    }

    loadOrder()
  }, [trackingToken, location.state])

  if (loading) {
    return (
      <section className="content-page">
        <h1>Retrieving your order...</h1>
      </section>
    )
  }

  if (error || !order) {
    return (
      <section className="content-page">
        <h1>Order not found</h1>
        <p>{error || 'We could not find this order.'}</p>
        <Link to="/shop" className="button button-primary">
          Return to shop
        </Link>
      </section>
    )
  }

  return (
    <section className="order-confirmation">
      <span className="eyebrow">THANK YOU</span>
      <h1>Your order has been received!</h1>
      <p>
        Your order is currently being processed. Keep your tracking
        link to check its status later.
      </p>

      <div className="order-confirmation-card">
        <h2>Order #{order.id}</h2>

        <p>
          Status: <strong>{order.status}</strong>
        </p>

        <p>
          Order total:{' '}
          <strong>KSh {Number(order.total_amount).toFixed(2)}</strong>
        </p>

        <h3>Items ordered</h3>

        {order.items?.map((item, index) => (
          <div className="checkout-summary-item" key={item.product_name + index}>
            <span>
              {item.product_name} × {item.quantity}
            </span>
            <strong>
              KSh {Number(item.subtotal).toFixed(2)}
            </strong>
          </div>
        ))}

        <div className="tracking-link-section">
          <p>Your private order tracking link:</p>
          <input
            type="text"
            readOnly
            value={window.location.href}
            onFocus={(event) => event.target.select()}
          />
          <button
            type="button"
            className="product-add-button"
            onClick={() => navigator.clipboard.writeText(window.location.href)}
          >
            Copy tracking link
          </button>
        </div>
      </div>

      <Link to="/shop" className="button button-primary">
        Continue shopping
      </Link>
    </section>
  )
}

export default OrderConfirmation
