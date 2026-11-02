import React, { useState, useEffect } from 'react';
import { Phone, PhoneOff, Mic, Play, Sparkles, Volume2, Globe, Radio } from 'lucide-react';

export default function CallControlPanel({
  targetPhone,
  onInitiateTwilioCall,
  onStartWebCall,
  onEndCall,
  callState,
  onRunSimulation
}) {
  const [phone, setPhone] = useState(targetPhone || '8977155678');
  const [callDuration, setCallDuration] = useState(0);

  useEffect(() => {
    let timer;
    if (callState.status === 'CONNECTED' || callState.status === 'IN_PROGRESS') {
      timer = setInterval(() => setCallDuration(prev => prev + 1), 1000);
    } else {
      setCallDuration(0);
    }
    return () => clearInterval(timer);
  }, [callState.status]);

  const formatTimer = (secs) => {
    const mins = Math.floor(secs / 60);
    const remaining = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remaining.toString().padStart(2, '0')}`;
  };

  const isCallActive = callState.status === 'CONNECTED' || callState.status === 'IN_PROGRESS' || callState.status === 'DIALING';

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>

      {/* Top Title & Status */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Radio size={18} color="#38BDF8" />
            Universal Outbound Telephony & Voice Controller
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            Autonomous Universal Agent: Automatically understands and speaks ANY language, dialect, or code-mixed style in real-time.
          </p>
        </div>

        {/* Live Call State Badge */}
        {isCallActive && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="waveform-container">
              <div className="wave-bar"></div>
              <div className="wave-bar"></div>
              <div className="wave-bar"></div>
              <div className="wave-bar"></div>
              <div className="wave-bar"></div>
              <div className="wave-bar"></div>
            </div>
            <div style={{
              background: 'rgba(34, 197, 94, 0.15)',
              border: '1px solid rgba(34, 197, 94, 0.4)',
              padding: '6px 14px',
              borderRadius: '8px',
              color: '#4ADE80',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.85rem',
              fontWeight: 600
            }}>
              LIVE {formatTimer(callDuration)}
            </div>
          </div>
        )}
      </div>

      {/* Main Input & Action Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(200px, 1.2fr) auto auto auto',
        gap: '12px',
        alignItems: 'center'
      }}>

        {/* Phone Input */}
        <div style={{ position: 'relative' }}>
          <span style={{
            position: 'absolute',
            left: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            fontSize: '0.85rem',
            color: 'var(--text-dim)',
            fontWeight: 500
          }}>
            +91
          </span>
          <input
            type="text"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            disabled={isCallActive}
            placeholder="Enter 10-digit mobile number"
            style={{
              width: '100%',
              background: 'rgba(15, 23, 42, 0.9)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '10px',
              padding: '12px 14px 12px 48px',
              color: '#FFFFFF',
              fontSize: '0.95rem',
              fontFamily: 'var(--font-mono)',
              outline: 'none'
            }}
          />
        </div>

        {/* Gemini 3.1 Flash Live Active Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%)',
          border: '1px solid rgba(56, 189, 248, 0.4)',
          borderRadius: '10px',
          padding: '10px 14px'
        }}>
          <Globe size={16} color="#38BDF8" className="animate-spin-slow" />
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.78rem', color: '#38BDF8', fontWeight: 600 }}>
              Gemini 3.1 Flash Live
            </span>
            <span style={{ fontSize: '0.68rem', color: '#CBD5E1' }}>
              Native Speech-to-Speech (&lt; 300ms)
            </span>
          </div>
        </div>

        {/* Primary Call Buttons */}
        {!isCallActive ? (
          <>
            <button
              onClick={() => onInitiateTwilioCall(phone)}
              className="btn-primary"
              title="Call via Twilio Media Streams + Gemini 3.1 Flash Live (Native Audio-to-Audio)"
            >
              <Phone size={17} />
              <span>Dial via Gemini 3.1 Live</span>
            </button>

            <button
              onClick={() => onStartWebCall(phone)}
              className="btn-whatsapp"
              title="Start real-time audio conversation directly in your browser"
            >
              <Mic size={17} />
              <span>Web Voice Call</span>
            </button>
          </>
        ) : (
          <button
            onClick={onEndCall}
            style={{
              background: 'linear-gradient(135deg, #DC2626 0%, #991B1B 100%)',
              color: '#FFFFFF',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              padding: '10px 24px',
              borderRadius: '10px',
              fontWeight: 600,
              fontSize: '0.9rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer'
            }}
          >
            <PhoneOff size={17} />
            <span>End Call & Send Summary</span>
          </button>
        )}

      </div>

      {/* Quick Scenario Simulators Row - Demonstrating Universal Multi-Language Understanding */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginTop: '16px',
        paddingTop: '16px',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        flexWrap: 'wrap'
      }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Sparkles size={13} color="#F59E0B" />
          Test Multi-Language & Code-Mixing Scenarios:
        </span>

        <button
          onClick={() => onRunSimulation('TANGLISH_HOT')}
          className="btn-secondary"
          style={{ fontSize: '0.75rem', padding: '5px 12px', borderColor: 'rgba(56, 189, 248, 0.3)' }}
        >
          🔄 Tanglish Mix (Telugu + English)
        </button>

        <button
          onClick={() => onRunSimulation('HINGLISH_WARM')}
          className="btn-secondary"
          style={{ fontSize: '0.75rem', padding: '5px 12px', borderColor: 'rgba(168, 85, 247, 0.3)' }}
        >
          🔄 Hinglish Mix (Hindi + English)
        </button>

        <button
          onClick={() => onRunSimulation('PURE_TELUGU')}
          className="btn-secondary"
          style={{ fontSize: '0.75rem', padding: '5px 12px' }}
        >
          🇮🇳 Pure Telugu (తెలుగు)
        </button>

        <button
          onClick={() => onRunSimulation('PURE_HINDI')}
          className="btn-secondary"
          style={{ fontSize: '0.75rem', padding: '5px 12px' }}
        >
          🇮🇳 Pure Hindi (हिंदी)
        </button>

        <button
          onClick={() => onRunSimulation('PURE_ENGLISH')}
          className="btn-secondary"
          style={{ fontSize: '0.75rem', padding: '5px 12px' }}
        >
          🇬🇧 Pure English
        </button>

        <button
          onClick={() => onRunSimulation('TAMIL_MIX')}
          className="btn-secondary"
          style={{ fontSize: '0.75rem', padding: '5px 12px' }}
        >
          🇮🇳 Tamil / Other Languages
        </button>
      </div>

    </div>
  );
}
