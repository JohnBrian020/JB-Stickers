
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { createOrder } from '../services/orderService'

function Checkout() {
  const { cartItems, cartTotal, clearCart } = useCart()
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
  })

  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    if (cartItems.length === 0) {
      setError('Your cart is empty.')
      return
    }

    setSubmitting(true)
    setError('')

    const orderData = {
      customer: formData,
      items: cartItems.map((item) => ({
        product_id: Number(item.id),
        quantity: Number(item.quantity),
      })),
    }

    try {
      const order = await createOrder(orderData)

      clearCart()

      navigate(`/order-confirmation/${order.tracking_token}`, {
        state: { order },
      })
    } catch (requestError) {
      setError(
        requestError.message ||
        'We could not place your order. Please try again.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  if (cartItems.length === 0) {
    return (
      <section className="content-page">
        <h1>Your cart is empty</h1>
        <p>Add products before proceeding to checkout.</p>
        <Link to="/shop" className="button button-primary">
          Browse products
        </Link>
      </section>
    )
  }

  return (
    <section className="checkout-page">
      <span className="eyebrow">ALMOST YOURS</span>
      <h1>Checkout</h1>
      <p>Enter your details to complete your order.</p>

      <div className="checkout-layout">
        <form className="checkout-form" onSubmit={handleSubmit}>
          <h2>Customer details</h2>

          <label htmlFor="name">Full name</label>
          <input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            minLength={2}
            maxLength={120}
            required
          />

          <label htmlFor="email">Email address</label>
          <input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <label htmlFor="phone">Phone number</label>
          <input
            id="phone"
            name="phone"
            type="tel"
            value={formData.phone}
            onChange={handleChange}
            minLength={7}
            maxLength={30}
            required
          />

          <label htmlFor="address">Delivery address</label>
          <textarea
            id="address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            minLength={5}
            rows={4}
            required
          />

          {error && (
            <p className="checkout-error" role="alert">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="product-add-button"
            disabled={submitting}
          >
            {submitting ? 'Placing order...' : 'Place order'}
          </button>

          <Link to="/cart" className="back-to-shop">
            ← Back to cart
          </Link>
        </form>

        <aside className="checkout-summary">
          <h2>Your order</h2>

          {cartItems.map((item) => (
            <div className="checkout-summary-item" key={item.id}>
              <span>
                {item.name} × {item.quantity}
              </span>
              <strong>
                KSh {(item.price * item.quantity).toFixed(2)}
              </strong>
            </div>
          ))}

          <div className="cart-total">
            <span>Estimated total</span>
            <strong>KSh {cartTotal.toFixed(2)}</strong>
          </div>

          <p className="checkout-note">
            Final prices and stock availability are verified when your
            order is submitted.
          </p>
        </aside>
      </div>
    </section>
  )
}

export default Checkout
