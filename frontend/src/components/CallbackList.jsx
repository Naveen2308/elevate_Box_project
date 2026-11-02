import React from 'react';
import { Calendar, Clock, Phone, AlertCircle } from 'lucide-react';

export default function CallbackList({ callbacks }) {
  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Calendar size={17} color="#F59E0B" />
          Scheduled Callbacks from Speech ({callbacks.length})
        </h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Auto-parsed via NLP
        </span>
      </div>

      {callbacks.length === 0 ? (
        <div style={{
          textAlign: 'center',
          color: 'var(--text-dim)',
          padding: '24px 12px',
          fontSize: '0.85rem'
        }}>
          No callbacks scheduled yet. Say <em>"Call me tomorrow morning"</em> on the call to test!
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {callbacks.map((cb) => (
            <div
              key={cb.id}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '10px',
                padding: '12px 14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '8px'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#FBBF24', fontWeight: 600, fontSize: '0.85rem' }}>
                  <Clock size={14} />
                  <span>{cb.display_time}</span>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Spoken phrase: <em>"{cb.raw_input}"</em> • Reason: {cb.barrier_reason || 'Follow-up'}
                </div>
              </div>

              <div style={{
                background: 'rgba(245, 158, 11, 0.15)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                color: '#F59E0B',
                fontSize: '0.75rem',
                fontWeight: 600,
                padding: '4px 10px',
                borderRadius: '6px'
              }}>
                {cb.status}
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
