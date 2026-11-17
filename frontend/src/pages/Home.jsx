import { Link } from 'react-router-dom'

function Home() {
  return (
    <div className="home-page">
      <section className="hero-section">
        <div className="hero-badge">
          New Collection Available
        </div>

        <h1>
          Express Yourself with
          <span> Amazing Stickers</span>
        </h1>

        <p className="hero-description">
          Discover our collection of high-quality, creative
          stickers perfect for laptops, water bottles, notebooks,
          and more. Make every surface uniquely yours.
        </p>

        <div className="hero-actions">
          <Link to="/shop" className="button button-primary">
            Shop Now
          </Link>

          <Link to="/about" className="button button-secondary">
            Learn More
          </Link>
        </div>
      </section>

      <section className="home-features">
        <div className="section-heading">
          <span className="eyebrow">WHY CHOOSE US</span>
          <h2>Make Every Surface Yours</h2>
          <p>Little details. Big personality.</p>
        </div>

        <div className="feature-grid">
          <article className="feature-card">
            <span className="feature-icon">✦</span>
            <h3>Creative Designs</h3>
            <p>
              Unique designs that help you express your personality.
            </p>
          </article>

          <article className="feature-card">
            <span className="feature-icon">♡</span>
            <h3>Quality Stickers</h3>
            <p>
              Carefully selected stickers for your favourite surfaces.
            </p>
          </article>

          <article className="feature-card">
            <span className="feature-icon">➜</span>
            <h3>Easy Ordering</h3>
            <p>
              Browse, add to cart and place your order with ease.
            </p>
          </article>
        </div>
      </section>

      <section className="home-cta">
        <div>
          <span className="eyebrow">FIND YOUR STYLE</span>
          <h2>Your next favourite sticker is waiting.</h2>
        </div>

        <Link to="/shop" className="button button-primary">
          Explore Collection
        </Link>
      </section>
    </div>
  )
}

export default Home