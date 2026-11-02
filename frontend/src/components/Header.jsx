import React from 'react';
import { PhoneCall, ShieldCheck, Zap, SlidersHorizontal, MessageSquareCode } from 'lucide-react';

export default function Header({ config, onOpenSettings, isConnected }) {
  return (
    <header className="glass-panel" style={{ padding: '16px 28px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>

        {/* Logo & Studio Info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #0284C7 0%, #6366F1 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(2, 132, 199, 0.4)'
          }}>
            <PhoneCall size={22} color="#FFFFFF" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em', color: '#FFFFFF' }}>
                elevate<span style={{ color: '#38BDF8' }}>box</span>
              </h1>
              <span style={{
                fontSize: '0.65rem',
                fontWeight: 700,
                background: 'rgba(56, 189, 248, 0.15)',
                color: '#38BDF8',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                padding: '2px 8px',
                borderRadius: '6px',
                letterSpacing: '0.05em'
              }}>
                SDE INTERN SYSTEM
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Autonomous AI Voice & WhatsApp Calling Engine • Banjara Hills, Hyderabad
            </p>
          </div>
        </div>

        {/* Status Indicators & Action Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>

          {/* Target Lead Badge */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '6px 14px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Target:</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#38BDF8', fontFamily: 'var(--font-mono)' }}>
              +91 {config?.target_phone_number || '8977155678'}
            </span>
          </div>

          {/* Telephony Connection Status */}
          <div className="pulse-badge" style={{
            background: isConnected ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            color: isConnected ? '#4ADE80' : '#F87171',
            border: `1px solid ${isConnected ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
          }}>
            <span className="pulse-dot" style={{ background: isConnected ? '#22C55E' : '#EF4444' }} />
            {isConnected ? 'System Live' : 'Connecting'}
          </div>

          {/* Settings Modal Button */}
          <button
            onClick={onOpenSettings}
            className="btn-secondary"
            title="Configure Twilio & WhatsApp Cloud API Keys"
          >
            <SlidersHorizontal size={15} />
            <span>API Keys & Config</span>
          </button>

        </div>
      </div>
    </header>
  );
}
