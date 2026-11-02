import React from 'react';
import { Flame, Clock, Snowflake, CheckCircle2, AlertCircle, ShoppingBag, DollarSign, Calendar, Layers, ShieldAlert } from 'lucide-react';

export default function LeadMatrix({ intentData, qualification }) {
  const currentIntent = intentData?.intent || 'COLD';
  const confidence = Math.round((intentData?.confidence || 0.5) * 100);
  const reason = intentData?.reason || 'Initial qualification stage';

  const getIntentBadge = () => {
    switch (currentIntent) {
      case 'HOT':
        return {
          label: 'HOT LEAD - HIGH INTENT',
          icon: <Flame size={16} color="#EF4444" />,
          color: '#EF4444',
          bg: 'rgba(239, 68, 68, 0.15)',
          border: 'rgba(239, 68, 68, 0.4)',
          actionNote: '🔥 WhatsApp proposal dispatched mid-call!'
        };
      case 'WARM':
        return {
          label: 'WARM LEAD - INTERESTED',
          icon: <Clock size={16} color="#F59E0B" />,
          color: '#F59E0B',
          bg: 'rgba(245, 158, 11, 0.15)',
          border: 'rgba(245, 158, 11, 0.4)',
          actionNote: '⚡ Callback scheduled from spoken time!'
        };
      default:
        return {
          label: 'COLD LEAD - CASUAL / INQUIRY',
          icon: <Snowflake size={16} color="#38BDF8" />,
          color: '#38BDF8',
          bg: 'rgba(56, 189, 248, 0.15)',
          border: 'rgba(56, 189, 248, 0.4)',
          actionNote: '❄️ Informational brochure logged.'
        };
    }
  };

  const badge = getIntentBadge();

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      
      {/* Matrix Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={17} color="#38BDF8" />
          Lead Qualification & Intent Matrix
        </h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Confidence: <strong style={{ color: '#FFFFFF' }}>{confidence}%</strong>
        </span>
      </div>

      {/* Primary Intent Badge */}
      <div style={{
        background: badge.bg,
        border: `1px solid ${badge.border}`,
        borderRadius: '12px',
        padding: '14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: badge.color, fontWeight: 700, fontSize: '0.85rem' }}>
            {badge.icon}
            <span>{badge.label}</span>
          </div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            ElevateBox AI
          </span>
        </div>
        <p style={{ fontSize: '0.78rem', color: '#E2E8F0', marginTop: '2px' }}>
          {reason}
        </p>
        <div style={{ fontSize: '0.72rem', color: badge.color, fontWeight: 600, marginTop: '4px' }}>
          {badge.actionNote}
        </div>
      </div>

      {/* Extracted Discovery Facts Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '10px',
        flex: 1
      }}>
        
        {/* Products */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '10px',
          padding: '10px 12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
            <ShoppingBag size={12} color="#38BDF8" />
            <span>PRODUCTS / STORE</span>
          </div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#FFFFFF', marginTop: '4px' }}>
            {qualification?.products || 'Under discussion'}
          </div>
        </div>

        {/* Budget */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '10px',
          padding: '10px 12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
            <DollarSign size={12} color="#22C55E" />
            <span>ESTIMATED BUDGET</span>
          </div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#FFFFFF', marginTop: '4px' }}>
            {qualification?.budget || 'Not specified'}
          </div>
        </div>

        {/* Timeline */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '10px',
          padding: '10px 12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
            <Calendar size={12} color="#F59E0B" />
            <span>LAUNCH TIMELINE</span>
          </div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#FFFFFF', marginTop: '4px' }}>
            {qualification?.timeline || 'Flexible'}
          </div>
        </div>

        {/* Barriers / Objections */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '10px',
          padding: '10px 12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
            <ShieldAlert size={12} color="#EC4899" />
            <span>BARRIER / HESITATION</span>
          </div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#FFFFFF', marginTop: '4px' }}>
            {qualification?.barrier || 'None detected'}
          </div>
        </div>

      </div>

      {/* Features Required */}
      <div style={{
        background: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '10px',
        padding: '10px 12px'
      }}>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginBottom: '4px' }}>
          PROPOSED FEATURES & STACK
        </div>
        <div style={{ fontSize: '0.8rem', color: '#CBD5E1', lineHeight: '1.4' }}>
          {qualification?.features || 'UPI Payments, High-speed Storefront, Automated Shipping'}
        </div>
      </div>

    </div>
  );
}
