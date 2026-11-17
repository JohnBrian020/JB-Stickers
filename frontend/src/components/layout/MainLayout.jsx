import { useState } from 'react'
import { NavLink, Outlet, Link } from 'react-router-dom'
import Footer from './Footer'
import { useCart } from '../../context/CartContext'

const navigation = [
  { name: 'Home', path: '/', icon: '⌂' },
  { name: 'Shop', path: '/shop', icon: '🛒' },
  { name: 'About', path: '/about', icon: '♙' },
  { name: 'Contact', path: '/contact', icon: '✉' },
]

function MainLayout() {
  const [lightMode, setLightMode] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const { cartCount } = useCart()

  return (
    <div
      className="app-shell"
      data-theme={lightMode ? 'light' : 'dark'}
    >
      <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
        <Link to="/" className="brand">
          <span className="brand-symbol">XOXO</span>
          <span className="brand-name">Stickers</span>
        </Link>

        <nav className="sidebar-navigation">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `nav-link ${isActive ? 'active' : ''}`
              }
              onClick={() => setMenuOpen(false)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <Link
            to="/cart"
            className="sidebar-action"
            onClick={() => setMenuOpen(false)}
          >
            <span className="nav-icon">🛒</span>
            <span>Cart ({cartCount})</span>
          </Link>

          <button
            className="sidebar-action theme-toggle"
            onClick={() => setLightMode(!lightMode)}
          >
            <span className="nav-icon">
              {lightMode ? '☾' : '☼'}
            </span>
            <span>{lightMode ? 'Dark Mode' : 'Light Mode'}</span>
          </button>
        </div>
      </aside>

      <div className="main-column">
        <header className="mobile-header">
          <Link to="/" className="brand">
            <span className="brand-symbol">XOXO</span>
            <span className="brand-name">Stickers</span>
          </Link>

          <button
            className="mobile-menu-button"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle navigation"
          >
            {menuOpen ? '✕' : '☰'}
          </button>
        </header>

        <main className="page-content">
          <Outlet />
        </main>

        <Footer />
      </div>

      {menuOpen && (
        <button
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setMenuOpen(false)}
        />
      )}
    </div>
  )
}

export default MainLayout