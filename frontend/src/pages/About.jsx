import { Link } from 'react-router-dom'

function About() {
  return (
    <section className="content-page">
      <span className="eyebrow">OUR STORY</span>

      <h1>More than just stickers.</h1>

      <p>
        Welcome to ❌⭕❌❌ Stickers, a place where small details
        make a big statement. We believe the things you choose to
        put around you should say something about who you are.
      </p>

      <p>
        Whether you want to add personality to your everyday items,
        brighten up your space, or find a design that feels like you,
        we're here to help you express yourself one sticker at a time.
      </p>

      <div className="feature-grid">
        <article className="feature-card">
          <span className="feature-icon" aria-hidden="true">🎨</span>
          <h3>Express yourself</h3>
          <p>
            Your style is personal. Find stickers that reflect your
            interests, personality, and creativity.
          </p>
        </article>

        <article className="feature-card">
          <span className="feature-icon" aria-hidden="true">✨</span>
          <h3>Make it yours</h3>
          <p>
            Give everyday belongings a little more character with
            designs that help them stand out.
          </p>
        </article>

        <article className="feature-card">
          <span className="feature-icon" aria-hidden="true">🛍️</span>
          <h3>Find your favourites</h3>
          <p>
            Explore our sticker collection and discover designs
            that match your taste.
          </p>
        </article>
      </div>

      <div className="home-cta">
        <div>
          <h2>Your next favourite sticker is waiting.</h2>
          <p>
            Take a look through the collection and find something
            that speaks to you.
          </p>
        </div>

        <Link to="/shop" className="button button-primary">
          Explore the shop
        </Link>
      </div>
    </section>
  )
}

export default About
