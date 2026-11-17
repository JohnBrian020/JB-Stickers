
import { Link } from 'react-router-dom'

function ProductCard({ product }) {
  const imageUrl = product.image_url

  return (
    <Link
      to={`/shop/${product.id}`}
      className="product-card-link"
      aria-label={`View ${product.name}`}
    >
      <article className="product-card">
        <div className="product-image-container">
          {imageUrl && (
            <img
              src={imageUrl}
              alt={product.name}
              className="product-image"
              loading="lazy"
              onError={(event) => {
                event.currentTarget.style.display = 'none'
                event.currentTarget.nextElementSibling.style.display = 'flex'
              }}
            />
          )}

          <div
            className="product-image-placeholder"
            style={{ display: imageUrl ? 'none' : 'flex' }}
          >
            <span>✦</span>
            <p>Product image unavailable</p>
          </div>

          {product.stock <= 0 && (
            <span className="stock-badge">Out of stock</span>
          )}
        </div>

        <div className="product-information">
          <span className="product-category">
            {product.category || 'Stickers'}
          </span>

          <h3>{product.name}</h3>

          <p className="product-description">
            {product.description || 'Discover this unique sticker design.'}
          </p>

          <div className="product-card-bottom">
            <span className="product-price">
              KSh {Number(product.price).toFixed(2)}
            </span>

            <span className="product-stock">
              {product.stock > 0
                ? `${product.stock} available`
                : 'Unavailable'}
            </span>
          </div>

          <span className="product-view-link">View product →</span>
        </div>
      </article>
    </Link>
  )
}

export default ProductCard
