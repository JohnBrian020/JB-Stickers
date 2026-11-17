
import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

function AdminLogin() {
  const { admin, loading, login } = useAuth()
  const navigate = useNavigate()

  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setSubmitting(true)

    try {
      await login(identifier.trim(), password)
      navigate('/admin/dashboard', { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Login failed.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <p>Checking administrator session...</p>
  }

  if (admin) {
    return <Navigate to="/admin/dashboard" replace />
  }

  return (
    <main className="admin-login-page">
      <form className="admin-login-form" onSubmit={handleSubmit}>
        <span className="eyebrow">XOXO STICKERS</span>

        <h1>Admin Login</h1>
        <p>Sign in to manage your store.</p>

        <label htmlFor="identifier">Email or username</label>
        <input
          id="identifier"
          type="text"
          value={identifier}
          onChange={(event) => setIdentifier(event.target.value)}
          autoComplete="username"
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />

        {error && (
          <p className="admin-login-error" role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          className="product-add-button"
          disabled={submitting}
        >
          {submitting ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </main>
  )
}

export default AdminLogin
