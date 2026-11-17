
import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'

function Cart() {
  const {
    cartItems,
    cartCount,
    cartTotal,
    updateQuantity,
    removeFromCart,
    clearCart,
  } = useCart()

  if (cartItems.length === 0) {
    return (
      <section className="content-page">
        <span className="eyebrow">YOUR SELECTION</span>
        <h1>Shopping Cart</h1>

        <div className="empty-shop">
          <span>🛒</span>
          <h2>Your cart is currently empty.</h2>
          <p>Discover something you love and add it to your cart.</p>

          <Link to="/shop" className="button button-primary">
            Start Shopping
          </Link>
        </div>
      </section>
    )
  }

  return (
    <section className="cart-page">
      <span className="eyebrow">YOUR SELECTION</span>
      <h1>Shopping Cart</h1>
      <p>{cartCount} item(s) in your cart</p>

      <div className="cart-items">
        {cartItems.map((item) => (
          <article className="cart-item" key={item.id}>
            <div className="cart-item-image">
              {item.image_url ? (
                <img
                  src={item.image_url}
                  alt={item.name}
                  onError={(event) => {
                    event.currentTarget.style.display = 'none'
                    event.currentTarget.nextElementSibling.style.display = 'flex'
                  }}
                />
              ) : null}

              <div
                className="product-image-placeholder"
                style={{ display: item.image_url ? 'none' : 'flex' }}
              >
                ✦
              </div>
            </div>

            <div className="cart-item-info">
              <h3>{item.name}</h3>
              <p>KSh {item.price.toFixed(2)} each</p>

              <div className="cart-item-controls">
                <label>
                  Quantity
                  <input
                    type="number"
                    min="1"
                    max={item.stock}
                    value={item.quantity}
                    onChange={(event) =>
                      updateQuantity(item.id, event.target.value)
                    }
                  />
                </label>

                <button
                  type="button"
                  className="remove-cart-item"
                  onClick={() => removeFromCart(item.id)}
                >
                  Remove
                </button>
              </div>
            </div>

            <strong className="cart-item-subtotal">
              KSh {(item.price * item.quantity).toFixed(2)}
            </strong>
          </article>
        ))}
      </div>

      <div className="cart-summary">
        <button
          type="button"
          className="remove-cart-item"
          onClick={clearCart}
        >
          Clear cart
        </button>

        <div className="cart-total">
          <span>Total</span>
          <strong>KSh {cartTotal.toFixed(2)}</strong>
        </div>

        <Link to="/checkout" className="product-add-button">
            Proceed to checkout
        </Link>
      </div>

      <Link to="/shop" className="back-to-shop">
        ← Continue shopping
      </Link>
    </section>
  )
}

export default Cart
