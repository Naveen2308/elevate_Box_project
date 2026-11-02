import React, { useState, useRef, useEffect } from 'react';
import { Bot, User, Mic, Send, Volume2, Sparkles, CheckCircle2, Zap } from 'lucide-react';

export default function LiveConsole({
  messages,
  onSendMessage,
  isRecording,
  onToggleRecord,
  midCallFired,
  isAudioPlaying
}) {
  const [inputText, setInputText] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, midCallFired]);

  const handleSend = (e) => {
    e?.preventDefault();
    if (!inputText.trim()) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const playAudio = (audioUrl) => {
    if (!audioUrl) return;
    const audio = new Audio(audioUrl);
    audio.play().catch(e => console.error("Audio playback error:", e));
  };

  return (
    <div className="glass-panel" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '560px',
      overflow: 'hidden'
    }}>

      {/* Console Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(15, 23, 42, 0.4)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Bot size={18} color="#38BDF8" />
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#FFFFFF' }}>
            Live Stream & Multilingual Transcript
          </h3>
        </div>

        {isAudioPlaying && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#38BDF8', fontSize: '0.75rem', fontWeight: 500 }}>
            <Volume2 size={14} className="animate-pulse" />
            <span>AI Speaking...</span>
          </div>
        )}
      </div>

      {/* Mid-Call WhatsApp Banner Notification */}
      {midCallFired && (
        <div className="animate-slide-down" style={{
          background: 'linear-gradient(90deg, rgba(34, 197, 94, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%)',
          borderBottom: '1px solid rgba(34, 197, 94, 0.4)',
          padding: '10px 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: '#4ADE80',
          fontSize: '0.8rem',
          fontWeight: 600
        }}>
          <Zap size={16} color="#22C55E" />
          <span>⚡ MID-CALL ACTION TRIGGERED: WhatsApp proposal dispatched to caller while on call!</span>
        </div>
      )}

      {/* Transcript Messages Container */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: 'var(--text-dim)',
            textAlign: 'center',
            padding: '20px'
          }}>
            <Bot size={36} color="rgba(255, 255, 255, 0.15)" style={{ marginBottom: '12px' }} />
            <p style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-muted)' }}>
              No active call in progress
            </p>
            <p style={{ fontSize: '0.8rem', maxWidth: '300px', marginTop: '6px' }}>
              Click <strong>"Dial via Twilio"</strong> to call 8977155678 or <strong>"Web Voice Call"</strong> to speak directly.
            </p>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isAI = msg.role === 'assistant' || msg.speaker === 'AI';
            return (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: isAI ? 'flex-start' : 'flex-end',
                  gap: '4px'
                }}
              >
                {/* Speaker Tag */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.7rem',
                  color: isAI ? '#38BDF8' : '#818CF8',
                  fontWeight: 600,
                  padding: '0 4px'
                }}>
                  {isAI ? <Bot size={12} /> : <User size={12} />}
                  <span>{isAI ? 'ElevateBox AI Voice' : 'Caller / Lead'}</span>
                  {msg.language && (
                    <span style={{
                      background: 'rgba(56, 189, 248, 0.12)',
                      border: '1px solid rgba(56, 189, 248, 0.25)',
                      padding: '1px 6px',
                      borderRadius: '4px',
                      color: '#38BDF8',
                      fontSize: '0.65rem',
                      fontWeight: 600
                    }}>
                      🌐 {msg.language.toUpperCase()}
                    </span>
                  )}
                </div>

                {/* Message Bubble */}
                <div style={{
                  maxWidth: '82%',
                  padding: '12px 16px',
                  borderRadius: isAI ? '4px 16px 16px 16px' : '16px 4px 16px 16px',
                  background: isAI
                    ? 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%)'
                    : 'linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%)',
                  border: `1px solid ${isAI ? 'rgba(255, 255, 255, 0.08)' : 'rgba(56, 189, 248, 0.3)'}`,
                  color: '#FFFFFF',
                  fontSize: '0.9rem',
                  lineHeight: '1.45',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                  position: 'relative'
                }}>
                  {msg.text || msg.content}

                  {/* Audio Replay icon if available */}
                  {msg.audioUrl && (
                    <button
                      onClick={() => playAudio(msg.audioUrl)}
                      style={{
                        background: 'rgba(56, 189, 248, 0.15)',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '4px 8px',
                        color: '#38BDF8',
                        fontSize: '0.7rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        marginTop: '8px',
                        cursor: 'pointer'
                      }}
                    >
                      <Volume2 size={12} /> Play Voice
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Interactive Utterance Input Bar */}
      <form onSubmit={handleSend} style={{
        padding: '14px 18px',
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(15, 23, 42, 0.6)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        {/* Mic Speech Recognition Button */}
        <button
          type="button"
          onClick={onToggleRecord}
          style={{
            background: isRecording ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.08)',
            border: `1px solid ${isRecording ? '#EF4444' : 'rgba(255, 255, 255, 0.15)'}`,
            borderRadius: '10px',
            width: '42px',
            height: '42px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: isRecording ? '#EF4444' : '#FFFFFF',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          title={isRecording ? "Listening..." : "Click to speak via Microphone"}
        >
          <Mic size={18} className={isRecording ? 'animate-pulse' : ''} />
        </button>

        {/* Text Input for Telugu, Hindi or English */}
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Speak or type lead response (in Telugu, Hindi, or English)..."
          style={{
            flex: 1,
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '11px 16px',
            color: '#FFFFFF',
            fontSize: '0.88rem',
            outline: 'none'
          }}
        />

        {/* Send Button */}
        <button
          type="submit"
          className="btn-primary"
          style={{ padding: '10px 16px', borderRadius: '10px' }}
        >
          <Send size={16} />
        </button>
      </form>

    </div>
  );
}
