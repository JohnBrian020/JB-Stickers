import { useEffect, useState } from 'react'
import ProductGrid from '../components/products/ProductGrid'
import { getProducts } from '../services/productService'

function Shop() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadProducts() {
      try {
        setLoading(true)
        setError('')

        const result = await getProducts()
        setProducts(result)
      } catch (err) {
        setError(err.message || 'Unable to load products.')
      } finally {
        setLoading(false)
      }
    }

    loadProducts()
  }, [])

  return (
    <section className="content-page shop-page">
      <span className="eyebrow">OUR COLLECTION</span>

      <h1>Shop All Stickers</h1>

      <p>
        Discover creative designs and find the perfect stickers
        to express yourself.
      </p>

      {loading && (
        <div className="shop-message">
          <div className="loading-spinner" />
          <p>Loading our stickers...</p>
        </div>
      )}

      {!loading && error && (
        <div className="shop-error">
          <h2>Unable to load products</h2>
          <p>{error}</p>
          <button
            className="button button-primary"
            onClick={() => window.location.reload()}
          >
            Try Again
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="shop-results">
            <span>{products.length} products available</span>
          </div>

          <ProductGrid products={products} />
        </>
      )}
    </section>
  )
}

export default Shop