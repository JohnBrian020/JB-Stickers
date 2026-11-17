import { useEffect, useState } from 'react'
import { apiRequest } from '../../services/api'

const dashboardCards = [
  {
    key: 'total_orders',
    label: 'Total Orders',
  },
  {
    key: 'pending_orders',
    label: 'Pending Orders',
  },
  {
    key: 'completed_orders',
    label: 'Completed Orders',
  },
  {
    key: 'cancelled_orders',
    label: 'Cancelled Orders',
  },
]

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchDashboardStats() {
      try {
        const response = await apiRequest('/admin/dashboard')
        setStats(response.data)
      } catch (requestError) {
        setError(requestError.message || 'Failed to load dashboard.')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardStats()
  }, [])

  if (loading) {
    return <p>Loading dashboard...</p>
  }

  if (error) {
    return <p className="admin-error" role="alert">{error}</p>
  }

  if (!stats) {
    return <p>No dashboard data available.</p>
  }

  return (
    <section className="admin-dashboard">
      <div className="admin-page-heading">
        <h2>Dashboard Overview</h2>
        <p>Here's what's happening in your store.</p>
      </div>

      <div className="admin-stats-grid">
        {dashboardCards.map((card) => (
          <article className="admin-stat-card" key={card.key}>
            <p>{card.label}</p>
            <h3>{stats[card.key] ?? 0}</h3>
          </article>
        ))}
      </div>

      <article className="admin-revenue-card">
        <p>Total Order Value</p>
        <h2>
          KSh {Number(stats.total_order_value || 0).toLocaleString('en-KE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </h2>
        <span>Excludes cancelled orders</span>
      </article>
    </section>
  )
}

export default Dashboard