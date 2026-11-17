
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function AdminRoute() {
  const { admin, loading } = useAuth()

  if (loading) {
    return <p>Checking administrator session...</p>
  }

  if (!admin) {
    return <Navigate to="/admin/login" replace />
  }

  return <Outlet />
}

export default AdminRoute
