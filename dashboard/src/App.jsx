import React, { useState } from 'react'
import LoginForm     from './components/LoginForm'
import StudentHeader  from './components/StudentHeader'
import BalanceCard    from './components/BalanceCard'
import MovementsTable from './components/MovementsTable'
import AccessTimeline from './components/AccessTimeline'

function SkeletonLayout() {
  return (
    <div className="app-container">
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div className="skeleton skeleton-avatar" />
        <div style={{ flex: 1 }}>
          <div className="skeleton skeleton-line wide" />
          <div className="skeleton skeleton-line short" />
        </div>
      </div>
      <div className="card">
        <div className="skeleton skeleton-line short" style={{ marginBottom: 16 }} />
        <div className="skeleton skeleton-block" style={{ height: 60 }} />
        <div className="skeleton skeleton-line short" style={{ width: '20%', marginTop: 12 }} />
      </div>
      <div className="card">
        <div className="skeleton skeleton-line short" style={{ marginBottom: 20 }} />
        <div className="skeleton skeleton-line full" />
        <div className="skeleton skeleton-line full" />
        <div className="skeleton skeleton-line full" />
        <div className="skeleton skeleton-line wide" />
      </div>
      <div className="card">
        <div className="skeleton skeleton-line short" style={{ marginBottom: 20 }} />
        <div className="skeleton skeleton-line wide" />
        <div className="skeleton skeleton-line wide" />
        <div className="skeleton skeleton-line short" />
      </div>
    </div>
  )
}

export default function App() {
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)
  const [data,    setData]    = useState(null)

  async function handleLogin(username, password) {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/scrape', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ username, password }),
      })
      const json = await res.json()
      if (!res.ok) {
        setError(json.detail || 'Error al consultar el portal.')
        return
      }
      setData(json)
    } catch {
      setError('No se pudo conectar al servidor. Intenta de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  function handleLogout() {
    setData(null)
    setError(null)
  }

  // Loading skeleton while scraping
  if (loading) return <SkeletonLayout />

  // Show login form if no data yet
  if (!data) {
    return <LoginForm onSubmit={handleLogin} loading={loading} error={error} />
  }

  const { student, wallet, movements, access_logs, scraped_at } = data

  return (
    <div className="app-container">
      <StudentHeader student={student} scraped_at={scraped_at} onLogout={handleLogout} />
      <BalanceCard    wallet={wallet} />
      <MovementsTable movements={movements} />
      <AccessTimeline access_logs={access_logs} />
    </div>
  )
}
