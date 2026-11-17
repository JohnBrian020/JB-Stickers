
import { useEffect, useMemo, useState } from 'react'
import {
  getAdminProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from '../../services/productService'

const initialForm = {
  name: '',
  description: '',
  price: '',
  image_url: '',
  category: '',
  stock: '0',
  is_active: true,
}

function ManageProducts() {
  const [products, setProducts] = useState([])
  const [form, setForm] = useState(initialForm)
  const [editingId, setEditingId] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function loadProducts() {
    try {
      const result = await getAdminProducts()
      setProducts(result)
      setError('')
    } catch (err) {
      setError(err.message || 'Unable to load products.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let ignore = false

    async function fetchProducts() {
      try {
        const result = await getAdminProducts()

        if (!ignore) {
          setProducts(result)
          setError('')
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || 'Unable to load products.')
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    fetchProducts()

    return () => {
      ignore = true
    }
  }, [])
  
  const filteredProducts = useMemo(() => {
    return products.filter((product) =>
      product.name.toLowerCase().includes(search.toLowerCase())
    )
  }, [products, search])

  function handleChange(event) {
    const { name, value, type, checked } = event.target

    setForm((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  function resetForm() {
    setForm(initialForm)
    setEditingId(null)
  }

  function handleEdit(product) {
    setEditingId(product.id)

    setForm({
      name: product.name || '',
      description: product.description || '',
      price: String(product.price),
      image_url: product.image_url || '',
      category: product.category || '',
      stock: String(product.stock),
      is_active: product.is_active,
    })

    setMessage('')
    setError('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setSaving(true)
    setError('')
    setMessage('')

    const productData = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      price: Number(form.price),
      image_url: form.image_url.trim() || null,
      category: form.category.trim() || null,
      stock: Number(form.stock),
      is_active: form.is_active,
    }

    try {
      if (editingId) {
        await updateProduct(editingId, productData)
        setMessage('Product updated successfully.')
      } else {
        await createProduct(productData)
        setMessage('Product created successfully.')
      }

      resetForm()
      await loadProducts()
    } catch (err) {
      setError(err.message || 'Unable to save product.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(product) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${product.name}"?`
    )

    if (!confirmed) return

    setError('')
    setMessage('')

    try {
      await deleteProduct(product.id)
      setMessage('Product deleted successfully.')
      await loadProducts()
    } catch (err) {
      setError(err.message || 'Unable to delete product.')
    }
  }

  return (
    <section className="admin-products">
      <div className="admin-page-heading">
        <h2>Manage Products</h2>
        <p>Add, edit and manage your sticker collection.</p>
      </div>

      <form className="admin-product-form" onSubmit={handleSubmit}>
        <h3>{editingId ? 'Edit Product' : 'Add New Product'}</h3>

        <div className="admin-product-form-grid">
          <label>
            Product Name
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              required
              maxLength={120}
            />
          </label>

          <label>
            Category
            <input
              name="category"
              value={form.category}
              onChange={handleChange}
              placeholder="e.g. Aesthetic, Anime"
            />
          </label>

          <label>
            Price (KSh)
            <input
              name="price"
              type="number"
              min="0.01"
              step="0.01"
              value={form.price}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Stock Quantity
            <input
              name="stock"
              type="number"
              min="0"
              step="1"
              value={form.stock}
              onChange={handleChange}
              required
            />
          </label>

          <label className="admin-product-full-width">
            Image URL
            <input
              name="image_url"
              type="url"
              value={form.image_url}
              onChange={handleChange}
              placeholder="https://example.com/sticker.jpg"
            />
          </label>

          <label className="admin-product-full-width">
            Description
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              rows={3}
            />
          </label>

          <label className="admin-product-checkbox">
            <input
              name="is_active"
              type="checkbox"
              checked={form.is_active}
              onChange={handleChange}
            />
            Active (visible in the public shop)
          </label>
        </div>

        <div className="admin-product-form-actions">
          <button type="submit" disabled={saving}>
            {saving
              ? 'Saving...'
              : editingId
                ? 'Update Product'
                : 'Add Product'}
          </button>

          {editingId && (
            <button type="button" onClick={resetForm}>
              Cancel Edit
            </button>
          )}
        </div>
      </form>

      {message && (
        <p className="admin-success" role="status">{message}</p>
      )}

      {error && (
        <p className="admin-error" role="alert">{error}</p>
      )}

      <div className="admin-products-toolbar">
        <h3>Product Catalogue ({products.length})</h3>

        <input
          type="search"
          placeholder="Search products..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label="Search products"
        />
      </div>

      {loading ? (
        <p>Loading products...</p>
      ) : filteredProducts.length === 0 ? (
        <p>No products found.</p>
      ) : (
        <div className="admin-table-wrapper">
          <table className="admin-product-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {filteredProducts.map((product) => (
                <tr key={product.id}>
                  <td>
                    <strong>{product.name}</strong>
                    <small>#{product.id}</small>
                  </td>

                  <td>{product.category || 'Uncategorized'}</td>

                  <td>
                    KSh {Number(product.price).toFixed(2)}
                  </td>

                  <td>{product.stock}</td>

                  <td>
                    <span className={
                      product.is_active
                        ? 'admin-status-active'
                        : 'admin-status-inactive'
                    }>
                      {product.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>

                  <td>
                    <div className="admin-product-actions">
                      <button
                        type="button"
                        onClick={() => handleEdit(product)}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="admin-delete-button"
                        onClick={() => handleDelete(product)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default ManageProducts