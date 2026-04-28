import React from 'react'

/**
 * Formats a float to Venezuelan number convention using the de-DE locale:
 *   1742.69  →  "1.742,69 Bs"
 * de-DE uses '.' as thousands separator and ',' as decimal — same as Venezuela.
 * Do NOT use 'es-VE' — browser support is inconsistent across OSes.
 */
function formatBalanceVE(amount) {
  return (
    amount.toLocaleString('de-DE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }) + ' Bs'
  )
}

export default function BalanceCard({ wallet }) {
  return (
    <div className="card">
      {/* Label */}
      <div
        style={{
          fontSize: 11,
          letterSpacing: '0.08em',
          color: 'var(--text-secondary)',
          textTransform: 'uppercase',
          marginBottom: 12,
          fontWeight: 500,
        }}
      >
        Saldo Disponible
      </div>

      {/* Balance amount */}
      <div
        style={{
          fontSize: 56,
          fontWeight: 700,
          color: 'var(--accent-blue)',
          lineHeight: 1.05,
          letterSpacing: '-0.02em',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {formatBalanceVE(wallet.balance_bs)}
      </div>

      {/* Status row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          marginTop: 16,
          fontSize: 13,
          color: 'var(--text-secondary)',
        }}
      >
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: 'var(--accent-green)',
            display: 'inline-block',
            flexShrink: 0,
          }}
        />
        Actualizado hoy
      </div>
    </div>
  )
}
