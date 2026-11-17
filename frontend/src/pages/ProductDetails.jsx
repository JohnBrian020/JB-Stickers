import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getProductById } from '../services/productService'
import { useCart } from '../context/CartContext'

function ProductDetails() {
  const { productId } = useParams()
  const { addToCart } = useCart()
  const [added, setAdded] = useState(false)

  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadProduct() {
      try {
        setLoading(true)
        setError('')

        const data = await getProductById(productId)
        setProduct(data)
      } catch (err) {
        setError(err.message || 'Unable to load this product.')
      } finally {
        setLoading(false)
      }
    }

    loadProduct()
  }, [productId])

  if (loading) {
    return <div className="shop-message">Loading product...</div>
  }

  if (error || !product) {
    return (
      <section className="shop-message">
        <h2>Product not found</h2>
        <p>{error || 'This product may no longer be available.'}</p>
        <Link to="/shop">Return to shop</Link>
      </section>
    )
  }

  return (
    <section className="product-details-page">
      <Link to="/shop" className="back-to-shop">
        ← Back to shop
      </Link>

      <div className="product-details">
        <div className="product-details-image">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              onError={(event) => {
                event.currentTarget.style.display = 'none'
                event.currentTarget.nextElementSibling.style.display = 'flex'
              }}
            />
          ) : null}

          <div
            className="product-image-placeholder"
            style={{ display: product.image_url ? 'none' : 'flex' }}
          >
            <span>✦</span>
            <p>Product image unavailable</p>
          </div>
        </div>

        <div className="product-details-information">
          <span className="product-category">
            {product.category || 'Stickers'}
          </span>

          <h1>{product.name}</h1>

          <p className="product-details-price">
            KSh {Number(product.price).toFixed(2)}
          </p>

          <p className="product-details-description">
            {product.description || 'Discover this unique sticker design.'}
          </p>

          <p className="product-stock">
            {product.stock > 0
              ? `${product.stock} available`
              : 'Currently out of stock'}
          </p>

          <button
            className="product-add-button"
            disabled={product.stock <= 0}
            type="button"
            onClick={() => {
                const success = addToCart(product)

                if (success) {
                setAdded(true)
                }
            }}
            >
            {product.stock <= 0
                ? 'Out of stock'
                : added
                ? 'Added to cart ✓'
                : 'Add to cart'}
            </button>

            {added && (
            <p>
                <Link to="/cart">View your shopping cart →</Link>
            </p>
            )}
        </div>
      </div>
    </section>
  )
}

export default ProductDetails
