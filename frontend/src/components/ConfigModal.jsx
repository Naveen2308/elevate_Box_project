import React, { useState, useEffect } from 'react';
import { X, Save, Key, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function ConfigModal({ isOpen, onClose, config, onSaveConfig }) {
  const [formData, setFormData] = useState({
    TWILIO_ACCOUNT_SID: '',
    TWILIO_AUTH_TOKEN: '',
    TWILIO_PHONE_NUMBER: '',
    WHATSAPP_TOKEN: '',
    WHATSAPP_PHONE_NUMBER_ID: '',
    GROQ_API_KEY: '',
    GEMINI_API_KEY: '',
    CANDIDATE_PHONE: '',
    TARGET_PHONE_NUMBER: ''
  });

  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (config) {
      setFormData({
        TWILIO_ACCOUNT_SID: config.TWILIO_ACCOUNT_SID || '',
        TWILIO_AUTH_TOKEN: config.TWILIO_AUTH_TOKEN || '',
        TWILIO_PHONE_NUMBER: config.TWILIO_PHONE_NUMBER || '',
        WHATSAPP_TOKEN: config.WHATSAPP_TOKEN || '',
        WHATSAPP_PHONE_NUMBER_ID: config.WHATSAPP_PHONE_NUMBER_ID || '',
        GROQ_API_KEY: config.GROQ_API_KEY || '',
        GEMINI_API_KEY: config.GEMINI_API_KEY || '',
        CANDIDATE_PHONE: config.candidate_phone || '8977155678',
        TARGET_PHONE_NUMBER: config.target_phone_number || '8977155678'
      });
    }
  }, [config, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onSaveConfig(formData);
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      onClose();
    }, 1200);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '560px',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '28px',
        background: '#0F172A',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        boxShadow: '0 20px 40px rgba(0,0,0,0.6)'
      }}>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Key size={20} color="#38BDF8" />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#FFFFFF' }}>
              Telephony & Cloud API Settings
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {savedSuccess && (
          <div style={{
            background: 'rgba(34, 197, 94, 0.15)',
            border: '1px solid rgba(34, 197, 94, 0.4)',
            color: '#4ADE80',
            padding: '10px 14px',
            borderRadius: '8px',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '0.85rem'
          }}>
            <CheckCircle2 size={16} />
            <span>Credentials updated and applied successfully!</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

          {/* Target & Candidate info */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                ElevateBox Target Phone
              </label>
              <input
                type="text"
                value={formData.TARGET_PHONE_NUMBER}
                onChange={(e) => setFormData({ ...formData, TARGET_PHONE_NUMBER: e.target.value })}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px',
                  color: '#FFFFFF',
                  fontSize: '0.85rem'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                Candidate Phone (For WhatsApp)
              </label>
              <input
                type="text"
                value={formData.CANDIDATE_PHONE}
                onChange={(e) => setFormData({ ...formData, CANDIDATE_PHONE: e.target.value })}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px',
                  color: '#FFFFFF',
                  fontSize: '0.85rem'
                }}
              />
            </div>
          </div>

          {/* Twilio Section */}
          <div style={{ paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#38BDF8', marginBottom: '8px' }}>
              Twilio Telephony (Free Trial)
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <input
                type="text"
                placeholder="Twilio Account SID (e.g. AC...)"
                value={formData.TWILIO_ACCOUNT_SID}
                onChange={(e) => setFormData({ ...formData, TWILIO_ACCOUNT_SID: e.target.value })}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px',
                  color: '#FFFFFF',
                  fontSize: '0.85rem'
                }}
              />
              <input
                type="password"
                placeholder="Twilio Auth Token"
                value={formData.TWILIO_AUTH_TOKEN}
                onChange={(e) => setFormData({ ...formData, TWILIO_AUTH_TOKEN: e.target.value })}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px',
                  color: '#FFFFFF',
                  fontSize: '0.85rem'
                }}
              />
              <input
                type="text"
                placeholder="Twilio Phone Number (e.g. +1234567890)"
                value={formData.TWILIO_PHONE_NUMBER}
                onChange={(e) => setFormData({ ...formData, TWILIO_PHONE_NUMBER: e.target.value })}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px',
                  color: '#FFFFFF',
                  fontSize: '0.85rem'
                }}
              />
            </div>
          </div>

          {/* WhatsApp Cloud API Section */}
          <div style={{ paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#22C55E', marginBottom: '8px' }}>
              Meta WhatsApp Cloud API (Graph API)
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <input
                type="password"
                placeholder="WhatsApp Permanent / User Access Token (EAAG...)"
                value={formData.WHATSAPP_TOKEN}
                onChange={(e) => setFormData({ ...formData, WHATSAPP_TOKEN: e.target.value })}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px',
                  color: '#FFFFFF',
                  fontSize: '0.85rem'
                }}
              />
              <input
                type="text"
                placeholder="WhatsApp Phone Number ID"
                value={formData.WHATSAPP_PHONE_NUMBER_ID}
                onChange={(e) => setFormData({ ...formData, WHATSAPP_PHONE_NUMBER_ID: e.target.value })}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px',
                  color: '#FFFFFF',
                  fontSize: '0.85rem'
                }}
              />
            </div>
          </div>

          {/* LLM Section */}
          <div style={{ paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#F59E0B', marginBottom: '8px' }}>
              LLM Decision Engine (Groq / Gemini Free Tier)
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <input
                type="password"
                placeholder="Groq API Key (gsk_...)"
                value={formData.GROQ_API_KEY}
                onChange={(e) => setFormData({ ...formData, GROQ_API_KEY: e.target.value })}
                style={{
                  width: '100%',
                  background: '#1E293B',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '10px',
                  color: '#FFFFFF',
                  fontSize: '0.85rem'
                }}
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', marginTop: '12px' }}
          >
            <Save size={16} />
            <span>Save Configuration</span>
          </button>

        </form>
      </div>
    </div>
  );
}
