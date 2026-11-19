
import { useCallback, useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { getTrackedOrder } from '../services/orderService'

const orderStatuses = [
  { value: 'pending', label: 'Order received', description: 'We have received your order.' },
  { value: 'confirmed', label: 'Confirmed', description: 'Your order has been confirmed.' },
  { value: 'processing', label: 'Processing', description: 'Your stickers are being prepared.' },
  { value: 'shipped', label: 'Shipped', description: 'Your order is on its way.' },
  { value: 'delivered', label: 'Delivered', description: 'Your order has been delivered.' },
]

function OrderConfirmation() {
  const { trackingToken } = useParams()
  const location = useLocation()

  const initialOrder = location.state?.order || null

  const [order, setOrder] = useState(initialOrder)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(!initialOrder)
  const [refreshing, setRefreshing] = useState(false)
  const [copied, setCopied] = useState(false)

  const refreshOrder = useCallback(async () => {
    setRefreshing(true)
    setError('')

    try {
      const orderData = await getTrackedOrder(trackingToken)
      setOrder(orderData)
    } catch (requestError) {
      setError(requestError.message || 'Could not refresh your order.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [trackingToken])

  useEffect(() => {
    let isActive = true

    async function loadOrder() {
      try {
        const orderData = await getTrackedOrder(trackingToken)

        if (isActive) {
          setOrder(orderData)
          setError('')
        }
      } catch (requestError) {
        if (isActive) {
          setError(
            requestError.message || 'Could not retrieve your order.'
          )
        }
      } finally {
        if (isActive) {
          setLoading(false)
        }
      }
    }

    loadOrder()

    return () => {
      isActive = false
    }
  }, [trackingToken])
  async function copyTrackingLink() {
    setCopied(false)

    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopied(true)
    } catch {
      setError('Could not copy the tracking link. Please copy it manually.')
    }
  }

  if (loading && !order) {
    return (
      <section className="content-page">
        <h1>Retrieving your order...</h1>
      </section>
    )
  }

  if (!order) {
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

  const currentStatus = String(order.status).toLowerCase()
  const currentIndex = orderStatuses.findIndex(
    (status) => status.value === currentStatus
  )
  const isCancelled = currentStatus === 'cancelled'

  return (
    <section className="order-confirmation">
      <span className="eyebrow">THANK YOU</span>
      <h1>Your order has been received!</h1>
      <p>
        Keep your private tracking link to check your order status
        whenever you need to.
      </p>

      <div className="order-confirmation-card">
        <div className="tracking-heading">
          <div>
            <h2>Order #{order.id}</h2>
            <p className="order-status-label">
              Current status: <strong>{currentStatus}</strong>
            </p>
          </div>

          <button
            type="button"
            className="product-add-button"
            onClick={refreshOrder}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Refresh status'}
          </button>
        </div>

        {error && (
          <p className="tracking-error" role="alert">
            {error}
          </p>
        )}

        {isCancelled ? (
          <div className="tracking-cancelled">
            <h3>Order cancelled</h3>
            <p>This order has been cancelled. Contact us if you need assistance.</p>
          </div>
        ) : (
          <div className="order-timeline">
            <h3>Order progress</h3>

            {orderStatuses.map((status, index) => {
              const isCompleted = currentIndex > index
              const isCurrent = currentIndex === index

              return (
                <div
                  className={`timeline-step ${
                    isCompleted ? 'completed' : ''
                  } ${isCurrent ? 'current' : ''}`}
                  key={status.value}
                >
                  <div className="timeline-marker">
                    {isCompleted ? '✓' : index + 1}
                  </div>

                  <div className="timeline-content">
                    <strong>{status.label}</strong>
                    <p>{status.description}</p>
                    {isCurrent && (
                      <span className="timeline-current-label">
                        Current status
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        <div className="order-summary-details">
          <p>
            Order total:{' '}
            <strong>
              KSh {Number(order.total_amount).toFixed(2)}
            </strong>
          </p>

          <h3>Items ordered</h3>

          {order.items?.map((item, index) => (
            <div
              className="checkout-summary-item"
              key={`${item.product_name}-${index}`}
            >
              <span>
                {item.product_name} × {item.quantity}
              </span>
              <strong>
                KSh {Number(item.subtotal).toFixed(2)}
              </strong>
            </div>
          ))}
        </div>

        <div className="tracking-link-section">
          <h3>Your private tracking link</h3>
          <p>Save this link so you can return to your order later.</p>

          <input
            type="text"
            readOnly
            value={window.location.href}
            onFocus={(event) => event.target.select()}
          />

          <button
            type="button"
            className="product-add-button"
            onClick={copyTrackingLink}
          >
            {copied ? 'Link copied!' : 'Copy tracking link'}
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

