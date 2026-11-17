import { NavLink } from 'react-router-dom'

function AdminSidebar() {
  return (
    <aside className="admin-sidebar">
      <div className="admin-brand">
        <h2>XOXO STICKERS</h2>
        <span>ADMIN PANEL</span>
      </div>

      <nav className="admin-navigation">
        <NavLink to="/admin/dashboard">
          Dashboard
        </NavLink>

        <NavLink to="/admin/orders">
          Manage Orders
        </NavLink>

        <NavLink to="/admin/products">
          Manage Products
        </NavLink>
      </nav>

      <div className="admin-sidebar-footer">
        <NavLink to="/">
          View Store
        </NavLink>
      </div>
    </aside>
  )
}

export default AdminSidebar