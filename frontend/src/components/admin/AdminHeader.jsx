import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

function AdminHeader() {
  const { admin, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/admin/login', { replace: true })
  }

  return (
    <header className="admin-header">
      <div>
        <h1>Admin Panel</h1>
        <p>Welcome, {admin?.username || 'Administrator'}</p>
      </div>

      <button type="button" onClick={handleLogout}>
        Logout
      </button>
    </header>
  )
}

export default AdminHeader