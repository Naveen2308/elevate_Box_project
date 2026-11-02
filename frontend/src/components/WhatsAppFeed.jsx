import React, { useState } from 'react';
import { Send, FileText, Image as ImageIcon, CheckCircle, ExternalLink, RefreshCw, MessageSquare, Zap, Layers } from 'lucide-react';

export default function WhatsAppFeed({ logs, onManualDispatch, targetPhone, candidatePhone }) {
  const [activeTab, setActiveTab] = useState('PREVIEW'); // 'PREVIEW' or 'LOGS'
  const [previewMode, setPreviewMode] = useState('POST_CALL'); // 'POST_CALL', 'MID_CALL', 'TEMPLATE'
  const [isSending, setIsSending] = useState(false);

  const handleSend = async (type) => {
    setIsSending(true);
    try {
      await onManualDispatch(type);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '100%' }}>

      {/* Header with Tabs */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '26px',
            height: '26px',
            borderRadius: '6px',
            background: 'linear-gradient(135deg, #22C55E 0%, #16A34A 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <MessageSquare size={15} color="#FFFFFF" />
          </div>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#FFFFFF' }}>
            Meta WhatsApp Cloud API Engine
          </h3>
        </div>

        {/* Tab switcher */}
        <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', padding: '3px', borderRadius: '8px' }}>
          <button
            onClick={() => setActiveTab('PREVIEW')}
            style={{
              background: activeTab === 'PREVIEW' ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
              color: activeTab === 'PREVIEW' ? '#4ADE80' : 'var(--text-muted)',
              border: 'none',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Package Preview
          </button>
          <button
            onClick={() => setActiveTab('LOGS')}
            style={{
              background: activeTab === 'LOGS' ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
              color: activeTab === 'LOGS' ? '#4ADE80' : 'var(--text-muted)',
              border: 'none',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Live Logs ({logs.length})
          </button>
        </div>
      </div>

      {activeTab === 'PREVIEW' ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto' }}>

          {/* Sub-mode selector */}
          <div style={{ display: 'flex', gap: '6px' }}>
            <button
              onClick={() => setPreviewMode('POST_CALL')}
              style={{
                flex: 1,
                padding: '6px 8px',
                borderRadius: '6px',
                border: '1px solid ' + (previewMode === 'POST_CALL' ? '#22C55E' : 'rgba(255,255,255,0.1)'),
                background: previewMode === 'POST_CALL' ? 'rgba(34, 197, 94, 0.15)' : 'rgba(0,0,0,0.2)',
                color: previewMode === 'POST_CALL' ? '#4ADE80' : 'var(--text-muted)',
                fontSize: '0.72rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Section 06 Follow-Up
            </button>
            <button
              onClick={() => setPreviewMode('MID_CALL')}
              style={{
                flex: 1,
                padding: '6px 8px',
                borderRadius: '6px',
                border: '1px solid ' + (previewMode === 'MID_CALL' ? '#F59E0B' : 'rgba(255,255,255,0.1)'),
                background: previewMode === 'MID_CALL' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(0,0,0,0.2)',
                color: previewMode === 'MID_CALL' ? '#FBBF24' : 'var(--text-muted)',
                fontSize: '0.72rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Mid-Call Proposal
            </button>
            <button
              onClick={() => setPreviewMode('TEMPLATE')}
              style={{
                flex: 1,
                padding: '6px 8px',
                borderRadius: '6px',
                border: '1px solid ' + (previewMode === 'TEMPLATE' ? '#38BDF8' : 'rgba(255,255,255,0.1)'),
                background: previewMode === 'TEMPLATE' ? 'rgba(56, 189, 248, 0.15)' : 'rgba(0,0,0,0.2)',
                color: previewMode === 'TEMPLATE' ? '#38BDF8' : 'var(--text-muted)',
                fontSize: '0.72rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Meta Template
            </button>
          </div>

          {/* WhatsApp Chat Simulation Bubble */}
          <div style={{
            background: 'linear-gradient(135deg, #075E54 0%, #128C7E 100%)',
            borderRadius: '12px',
            padding: '16px',
            color: '#FFFFFF',
            boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#A7F3D0', letterSpacing: '0.05em' }}>
                {previewMode === 'POST_CALL' && 'WHATSAPP DISPATCH PAYLOAD (SECTION 06)'}
                {previewMode === 'MID_CALL' && '⚡ HOT LEAD MID-CALL INSTANT DISPATCH'}
                {previewMode === 'TEMPLATE' && '📦 META BUSINESS TEMPLATE (OUTSIDE 24H)'}
              </span>
              <span style={{ fontSize: '0.7rem', color: '#D1FAE5' }}>
                To: +91 {targetPhone || '8977155678'}
              </span>
            </div>

            {previewMode === 'POST_CALL' && (
              <>
                <div style={{ fontSize: '0.85rem', lineHeight: '1.5', whiteSpace: 'pre-line', color: '#F0FDF4' }}>
                  {`Hi! Thank you for taking the time to speak with our AI system today.

Here is a summary of what we discussed for your upcoming e-commerce project:

📌 *Your Requirements & Specifics:*
• *Products/Category*: Custom E-Commerce Storefront
• *Key Features*: UPI, Razorpay & Automated Shipping
• *Stated Budget*: Discussed on call
• *Target Timeline*: 7-14 Day Delivery Window
• *Conversation Notes*: "Custom online store with high-speed mobile checkout"

💡 *Lead Classification*: WARM / HOT

👤 *Candidate Contact Information:*
• *Direct Mobile / WhatsApp*: +91 ${candidatePhone || '8977155678'}
• *Email*: candidate@elevatebox.com

Attached below are:
1️⃣ The System Architecture Diagram showing how this autonomous AI voice & WhatsApp engine is built.
2️⃣ My Resume for the SDE Intern role at ElevateBox.`}
                </div>

                {/* Media Attachments Cards */}
                <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>

                  {/* Architecture Diagram Card */}
                  <div style={{
                    background: 'rgba(0, 0, 0, 0.25)',
                    borderRadius: '8px',
                    padding: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    border: '1px solid rgba(255, 255, 255, 0.15)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <ImageIcon size={18} color="#38BDF8" />
                      <div>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#FFFFFF' }}>
                          architecture_diagram.png
                        </div>
                        <div style={{ fontSize: '0.7rem', color: '#A7F3D0' }}>
                          Flow from Call to Live WhatsApp Action
                        </div>
                      </div>
                    </div>
                    <a
                      href="/static/architecture_diagram.png"
                      target="_blank"
                      rel="noreferrer"
                      style={{ color: '#38BDF8', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', textDecoration: 'none' }}
                    >
                      <span>View</span>
                      <ExternalLink size={13} />
                    </a>
                  </div>

                  {/* Resume Card */}
                  <div style={{
                    background: 'rgba(0, 0, 0, 0.25)',
                    borderRadius: '8px',
                    padding: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    border: '1px solid rgba(255, 255, 255, 0.15)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FileText size={18} color="#FBBF24" />
                      <div>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#FFFFFF' }}>
                          SDE_Intern_Resume.pdf
                        </div>
                        <div style={{ fontSize: '0.7rem', color: '#A7F3D0' }}>
                          Candidate Qualifications & Stack
                        </div>
                      </div>
                    </div>
                    <a
                      href="/static/resume.pdf"
                      target="_blank"
                      rel="noreferrer"
                      style={{ color: '#FBBF24', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', textDecoration: 'none' }}
                    >
                      <span>View</span>
                      <ExternalLink size={13} />
                    </a>
                  </div>

                </div>
              </>
            )}

            {previewMode === 'MID_CALL' && (
              <div style={{ fontSize: '0.85rem', lineHeight: '1.5', whiteSpace: 'pre-line', color: '#F0FDF4' }}>
                {`⚡ *ElevateBox Instant Proposal & Demo Link*

Hi! While we are on this call, here is the immediate e-commerce launch blueprint:

• *Features Discussed*: UPI Payments, Instant Checkout & Mobile Optimized
• *Target Timeline*: 2 Weeks
• *Budget Alignment*: Under ₹50,000

🔗 *Live Demo Store*: https://elevatebox-demo-store.vercel.app
📄 *Instant Portfolio*: https://elevatebox.com/case-studies

Let's finalize the next steps on the call right now!`}
              </div>
            )}

            {previewMode === 'TEMPLATE' && (
              <div style={{ fontSize: '0.85rem', lineHeight: '1.5', whiteSpace: 'pre-line', color: '#F0FDF4' }}>
                {`📦 *Meta WhatsApp Template: jaspers_market_order_confirmation_v1*

*Customer*: ${candidatePhone || 'Naveen Peketi'}
*Order / Inquiry ID*: ELEVATE-2026
*Date*: Today

*Status*: Approved Meta Business Template for Outbound Messaging`}
              </div>
            )}
          </div>

          {/* Test Dispatch Button */}
          <button
            onClick={() => handleSend(previewMode)}
            disabled={isSending}
            className="btn-whatsapp"
            style={{ width: '100%', justifyContent: 'center', marginTop: 'auto', opacity: isSending ? 0.7 : 1 }}
          >
            <Send size={15} />
            <span>
              {isSending ? 'Dispatching...' : `Test Dispatch (${previewMode}) to ${targetPhone}`}
            </span>
          </button>

        </div>
      ) : (
        /* Logs view */
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {logs.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '40px 0', fontSize: '0.85rem' }}>
              No WhatsApp messages dispatched yet.
            </div>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px 12px',
                  fontSize: '0.8rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, color: '#4ADE80' }}>{log.type}</span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    To: {log.recipient}
                  </span>
                </div>
                <div style={{ color: '#CBD5E1', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                  Status: {log.status_code === 200 ? '200 OK (Dispatched)' : `Code ${log.status_code}`}
                </div>
                {log.response && (
                  <pre style={{
                    marginTop: '6px',
                    padding: '6px',
                    background: 'rgba(0,0,0,0.3)',
                    borderRadius: '4px',
                    fontSize: '0.68rem',
                    color: '#94A3B8',
                    overflowX: 'auto',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {JSON.stringify(log.response, null, 2)}
                  </pre>
                )}
              </div>
            ))
          )}
        </div>
      )}

    </div>
  );
}
