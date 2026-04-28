import React, { useState } from 'react'

export default function LoginForm({ onSubmit, loading, error }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (username.trim() && password.trim()) {
      onSubmit(username.trim(), password.trim())
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
        background: 'var(--bg)',
      }}
    >
      <div
        className="card"
        style={{ width: '100%', maxWidth: 400 }}
      >
        {/* Logo / title */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: 'var(--accent-blue)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 28,
              marginBottom: 16,
            }}
          >
            🅿
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>
            Zona U · Estacionamiento
          </h1>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginTop: 6 }}>
            Ingresa con tus credenciales UCAB
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Username */}
          <div>
            <label
              htmlFor="username"
              style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', display: 'block', marginBottom: 6, letterSpacing: '0.04em', textTransform: 'uppercase' }}
            >
              Usuario UCAB
            </label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="tu.usuario"
              disabled={loading}
              style={{
                width: '100%',
                padding: '11px 14px',
                borderRadius: 10,
                border: '1.5px solid #E5E5E5',
                fontSize: 15,
                fontFamily: 'var(--font)',
                outline: 'none',
                boxSizing: 'border-box',
                background: loading ? '#FAFAFA' : '#fff',
                color: 'var(--text-primary)',
                transition: 'border-color 0.15s',
              }}
              onFocus={e => (e.target.style.borderColor = 'var(--accent-blue)')}
              onBlur={e => (e.target.style.borderColor = '#E5E5E5')}
            />
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', display: 'block', marginBottom: 6, letterSpacing: '0.04em', textTransform: 'uppercase' }}
            >
              Contraseña
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
              style={{
                width: '100%',
                padding: '11px 14px',
                borderRadius: 10,
                border: '1.5px solid #E5E5E5',
                fontSize: 15,
                fontFamily: 'var(--font)',
                outline: 'none',
                boxSizing: 'border-box',
                background: loading ? '#FAFAFA' : '#fff',
                color: 'var(--text-primary)',
                transition: 'border-color 0.15s',
              }}
              onFocus={e => (e.target.style.borderColor = 'var(--accent-blue)')}
              onBlur={e => (e.target.style.borderColor = '#E5E5E5')}
            />
          </div>

          {/* Error */}
          {error && (
            <div
              style={{
                background: '#FFF1F0',
                border: '1px solid #FFCCC7',
                borderRadius: 10,
                padding: '10px 14px',
                fontSize: 14,
                color: 'var(--accent-red)',
              }}
            >
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || !username.trim() || !password.trim()}
            style={{
              background: loading ? '#A0C4FF' : 'var(--accent-blue)',
              color: '#fff',
              border: 'none',
              borderRadius: 12,
              padding: '13px 0',
              fontSize: 15,
              fontWeight: 600,
              fontFamily: 'var(--font)',
              cursor: loading ? 'not-allowed' : 'pointer',
              width: '100%',
              marginTop: 4,
              transition: 'background 0.15s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
            }}
          >
            {loading ? (
              <>
                <span className="dot-pulse" style={{ background: '#fff' }} />
                Consultando portal...
              </>
            ) : (
              'Consultar mi saldo'
            )}
          </button>
        </form>

        {/* Security note */}
        <p
          style={{
            fontSize: 12,
            color: 'var(--text-secondary)',
            textAlign: 'center',
            marginTop: 20,
            lineHeight: 1.6,
          }}
        >
          🔒 Tus credenciales se usan únicamente para consultar el portal y nunca se almacenan.
        </p>
      </div>
    </div>
  )
}
