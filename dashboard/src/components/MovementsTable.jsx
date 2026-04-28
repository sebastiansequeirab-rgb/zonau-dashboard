import React, { useState } from 'react'

const PAGE_SIZE = 10

function formatAmountVE(amount) {
  const abs = Math.abs(amount)
  return (
    abs.toLocaleString('de-DE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }) + ' Bs'
  )
}

const thStyle = {
  padding: '8px 24px',
  textAlign: 'left',
  fontWeight: 500,
  fontSize: 11,
  letterSpacing: '0.06em',
  color: 'var(--text-secondary)',
  textTransform: 'uppercase',
  borderBottom: '1px solid #F0F0F0',
}

const tdStyle = {
  padding: '13px 24px',
  borderBottom: '1px solid #F0F0F0',
  verticalAlign: 'middle',
}

export default function MovementsTable({ movements }) {
  const [showAll, setShowAll] = useState(false)

  if (!movements || movements.length === 0) {
    return (
      <div className="card">
        <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>Movimientos</h2>
        <div
          style={{
            textAlign: 'center',
            color: 'var(--text-secondary)',
            padding: '40px 0',
            fontSize: 14,
          }}
        >
          <div style={{ fontSize: 32, marginBottom: 8 }}>📋</div>
          Sin movimientos registrados
        </div>
      </div>
    )
  }

  const displayed = showAll ? movements : movements.slice(0, PAGE_SIZE)
  const hasMore = movements.length > PAGE_SIZE

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '24px 24px 0' }}>
        <h2 style={{ fontSize: 20, fontWeight: 600 }}>Movimientos</h2>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 16 }}>
          <thead>
            <tr>
              <th style={thStyle}>Fecha</th>
              <th style={thStyle}>Descripción</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>Monto</th>
            </tr>
          </thead>
          <tbody>
            {displayed.map((m, i) => (
              <tr
                key={i}
                style={{ background: i % 2 === 0 ? '#fff' : '#FAFAFA' }}
              >
                {/* Date */}
                <td style={{ ...tdStyle, whiteSpace: 'nowrap' }}>
                  <div style={{ fontSize: 14, color: 'var(--text-primary)', fontVariantNumeric: 'tabular-nums' }}>
                    {m.date}
                  </div>
                </td>

                {/* Description */}
                <td style={{ ...tdStyle, fontSize: 14, color: 'var(--text-primary)', maxWidth: 260 }}>
                  {m.type === 'debit'
                    ? 'Entrada vehicular'
                    : m.description.length > 30
                      ? m.description.slice(0, 30) + '…'
                      : m.description}
                </td>

                {/* Amount */}
                <td style={{ ...tdStyle, textAlign: 'right' }}>
                  <span
                    style={{
                      color: m.type === 'credit' ? 'var(--accent-green)' : 'var(--accent-red)',
                      fontSize: 14,
                      fontWeight: 500,
                      fontVariantNumeric: 'tabular-nums',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {m.type === 'credit' ? '↑ +' : '↓ −'}{formatAmountVE(m.amount_bs)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {hasMore && (
        <div style={{ padding: '12px 24px', borderTop: '1px solid #F0F0F0' }}>
          <button
            onClick={() => setShowAll(prev => !prev)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--accent-blue)',
              fontSize: 14,
              fontWeight: 500,
              padding: 0,
              fontFamily: 'var(--font)',
            }}
          >
            {showAll ? 'Ver menos' : `Ver todos (${movements.length})`}
          </button>
        </div>
      )}
    </div>
  )
}
