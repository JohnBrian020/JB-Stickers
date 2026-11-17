import { Link } from 'react-router-dom'

function Footer() {
  return (
    <footer className="site-footer">
      <div>
        <strong>XOXO Stickers</strong>
        <p>Express yourself. One sticker at a time.</p>
      </div>

      <div className="footer-links">
        <Link to="/">Home</Link>
        <Link to="/shop">Shop</Link>
        <Link to="/about">About</Link>
        <Link to="/contact">Contact</Link>
      </div>

      <p className="copyright">
        © {new Date().getFullYear()} XOXO Stickers. All rights reserved.
      </p>
    </footer>
  )
}

export default Footer