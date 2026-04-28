import React from 'react'

function formatAmountVE(amount) {
  return (
    Math.abs(amount).toLocaleString('de-DE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }) + ' Bs'
  )
}

export default function AccessTimeline({ access_logs }) {
  if (!access_logs || access_logs.length === 0) {
    return (
      <div className="card">
        <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>Entradas al Parking</h2>
        <div
          style={{
            textAlign: 'center',
            color: 'var(--text-secondary)',
            padding: '40px 0',
            fontSize: 14,
          }}
        >
          Sin registros de entradas
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 20 }}>Entradas al Parking</h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {access_logs.map((log, i) => {
          const isLast = i === access_logs.length - 1
          return (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                paddingBottom: isLast ? 0 : 14,
                marginBottom: isLast ? 0 : 14,
                borderBottom: isLast ? 'none' : '1px solid #F0F0F0',
              }}
            >
              {/* Dot */}
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: 'var(--accent-blue)',
                  display: 'inline-block',
                  flexShrink: 0,
                }}
              />

              {/* Date */}
              <div
                style={{
                  background: '#F0F0F0',
                  borderRadius: 8,
                  padding: '4px 10px',
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  whiteSpace: 'nowrap',
                  flexShrink: 0,
                  fontVariantNumeric: 'tabular-nums',
                }}
              >
                {log.date}
              </div>

              {/* Label */}
              <div style={{ flex: 1, fontSize: 14, color: 'var(--text-primary)' }}>
                Plan Estacionamiento Diario
              </div>

              {/* Amount charged */}
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 500,
                  color: 'var(--accent-red)',
                  whiteSpace: 'nowrap',
                  fontVariantNumeric: 'tabular-nums',
                }}
              >
                − {formatAmountVE(log.amount_bs)}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
