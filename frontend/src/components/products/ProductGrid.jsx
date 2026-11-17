import ProductCard from './ProductCard'

function ProductGrid({ products }) {
  if (!products.length) {
    return (
      <div className="empty-shop">
        <span>✦</span>
        <h2>No products found</h2>
        <p>Check back later for new sticker designs.</p>
      </div>
    )
  }

  return (
    <div className="product-grid">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  )
}

export default ProductGrid