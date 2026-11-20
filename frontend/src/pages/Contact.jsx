import { Link } from 'react-router-dom'

function Contact() {
  return (
    <section className="content-page">
      <span className="eyebrow">WE'RE HERE TO HELP</span>

      <h1>Let's talk.</h1>

      <p>
        Have a question about a sticker, need help with an order,
        or just want to get in touch? We'd love to hear from you.
      </p>

      <div className="feature-grid">
        <article className="feature-card">
          <span className="feature-icon" aria-hidden="true">✉️</span>
          <h3>Send us an email</h3>
          <p>
            Reach out with questions about products, orders, or anything
            else you'd like to know.
          </p>
          <a
            href="mailto:jeybee6713@gmail.com"
            className="button button-primary"
          >
            Email us
          </a>
          <p>jeybee6713@gmail.com</p>
        </article>

        <article className="feature-card">
          <span className="feature-icon" aria-hidden="true">💬</span>
          <h3>Chat on WhatsApp</h3>
          <p>
            Prefer messaging? Send us a WhatsApp message and we'll
            be happy to assist.
          </p>
          <a
            href="https://wa.me/254710709997"
            className="button button-primary"
            target="_blank"
            rel="noopener noreferrer"
          >
            Chat on WhatsApp
          </a>
          <p>+254 710 709 997</p>
        </article>

        <article className="feature-card">
          <span className="feature-icon" aria-hidden="true">📦</span>
          <h3>Need order help?</h3>
          <p>
            Have a question about an existing order? Message us on
            WhatsApp and include your order reference.
          </p>
          <a
            href="https://wa.me/254710709997"
            className="button button-primary"
            target="_blank"
            rel="noopener noreferrer"
          >
            Ask about an order
          </a>
        </article>
      </div>

      <div className="home-cta">
        <div>
          <h2>Ready to find your next favourite sticker?</h2>
          <p>Explore the collection and express yourself.</p>
        </div>

        <Link to="/shop" className="button button-primary">
          Browse stickers
        </Link>
      </div>
    </section>
  )
}

export default Contact
