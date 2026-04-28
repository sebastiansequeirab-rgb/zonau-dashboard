import React from 'react'

function formatTimestamp(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = n => String(n).padStart(2, '0')
  return (
    `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}`
  )
}

export default function StudentHeader({ student, scraped_at, onLogout }) {
  return (
    <div
      className="card"
      style={{ display: 'flex', alignItems: 'center', gap: 16 }}
    >
      {/* Avatar */}
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: '50%',
          background: 'var(--accent-blue)',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 20,
          fontWeight: 600,
          flexShrink: 0,
          letterSpacing: '-0.01em',
        }}
      >
        {student.initials}
      </div>

      {/* Name + subtitle */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: 17,
            fontWeight: 600,
            color: 'var(--text-primary)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {student.full_name}
        </div>
        <div style={{ fontSize: 14, color: 'var(--text-secondary)', marginTop: 2 }}>
          Zona U · UCAB
        </div>
      </div>

      {/* Last updated + logout */}
      <div style={{ textAlign: 'right', flexShrink: 0, lineHeight: 1.5 }}>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
          Actualizado
          <br />
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>
            {formatTimestamp(scraped_at)}
          </span>
        </div>
        {onLogout && (
          <button
            onClick={onLogout}
            style={{
              marginTop: 6,
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: 12,
              color: 'var(--accent-blue)',
              fontFamily: 'var(--font)',
              padding: 0,
            }}
          >
            Cerrar sesión
          </button>
        )}
      </div>
    </div>
  )
}
