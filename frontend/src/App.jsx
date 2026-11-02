import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import Header from './components/Header';
import CallControlPanel from './components/CallControlPanel';
import LiveConsole from './components/LiveConsole';
import LeadMatrix from './components/LeadMatrix';
import WhatsAppFeed from './components/WhatsAppFeed';
import CallbackList from './components/CallbackList';
import ConfigModal from './components/ConfigModal';

export default function App() {
  const [config, setConfig] = useState(null);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [callState, setCallState] = useState({ status: 'IDLE', sid: null, phone: '8977155678' });
  const [messages, setMessages] = useState([]);
  const [intentData, setIntentData] = useState({ intent: 'COLD', confidence: 0.5, reason: 'Ready to qualify lead' });
  const [qualification, setQualification] = useState({
    products: 'E-commerce Storefront',
    budget: 'Under discussion',
    timeline: 'Flexible',
    features: 'UPI Payments, High-speed Storefront, Automated Shipping',
    barrier: 'None'
  });
  const [midCallFired, setMidCallFired] = useState(false);
  const [whatsappLogs, setWhatsappLogs] = useState([]);
  const [callbacks, setCallbacks] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);

  const socketRef = useRef(null);
  const recognitionRef = useRef(null);
  const currentAudioRef = useRef(null);

  // Load initial backend config and data
  useEffect(() => {
    fetchConfig();
    fetchWhatsAppLogs();
    fetchCallbacks();
    initWebSocket();

    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      setConfig(data);
    } catch (e) {
      console.error('Failed to fetch config:', e);
    }
  };

  const fetchWhatsAppLogs = async () => {
    try {
      const res = await fetch('/api/whatsapp/logs');
      const data = await res.json();
      setWhatsappLogs(data.logs || []);
    } catch (e) {
      console.error('Failed to fetch WhatsApp logs:', e);
    }
  };

  const fetchCallbacks = async () => {
    try {
      const res = await fetch('/api/callbacks');
      const data = await res.json();
      setCallbacks(data.callbacks || []);
    } catch (e) {
      console.error('Failed to fetch callbacks:', e);
    }
  };

  // Initialize Real-time Dashboard WebSocket
  const initWebSocket = () => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/dashboard`;

    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log('Connected to Dashboard Telemetry WebSocket');
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          handleWebSocketEvent(payload);
        } catch (err) {
          console.error('Error parsing WS message:', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setTimeout(initWebSocket, 3000);
      };
    } catch (err) {
      console.error('WebSocket connection error:', err);
    }
  };

  const handleWebSocketEvent = (payload) => {
    const { event, data } = payload;
    if (event === 'CALL_STARTED' || event === 'CALL_INITIATED') {
      setCallState({ status: 'CONNECTED', sid: data.call_sid || data.session_id || data.stream_sid, phone: data.caller_phone || data.phone_number });
    } else if (event === 'CALL_ENDED') {
      setCallState({ status: 'COMPLETED', sid: null, phone: data.caller_phone });
      fetchWhatsAppLogs();
    } else if (event === 'TRANSCRIPT_UPDATE') {
      setMessages(prev => [...prev, data]);
    } else if (event === 'TURN_COMPLETED') {
      handleTurnCompleted(data);
    }
  };

  const handleTurnCompleted = (data) => {
    if (data.intent) {
      setIntentData({
        intent: data.intent,
        confidence: data.confidence,
        reason: data.reason
      });

      if (data.intent === 'HOT' || data.midcall_whatsapp_dispatched) {
        setMidCallFired(true);
        confetti({ particleCount: 80, spread: 60, origin: { y: 0.6 } });
        fetchWhatsAppLogs();
      }
    }

    if (data.qualification) {
      setQualification(prev => ({ ...prev, ...data.qualification }));
    }

    if (data.callback_scheduled) {
      fetchCallbacks();
    }

    if (data.audio_base64) {
      playAudio(data.audio_base64);
    }
  };

  const playAudio = (audioSrc) => {
    try {
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
      }
      const audio = new Audio(audioSrc);
      currentAudioRef.current = audio;
      setIsAudioPlaying(true);
      audio.onended = () => setIsAudioPlaying(false);
      audio.onerror = () => setIsAudioPlaying(false);
      audio.play().catch(e => console.log('Audio autoplay prevented:', e));
    } catch (e) {
      console.error('Audio play error:', e);
    }
  };

  // Dial via Twilio ConversationRelay
  const handleInitiateTwilioCall = async (phone) => {
    setCallState({ status: 'DIALING', sid: null, phone });
    try {
      const res = await fetch('/api/calls/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone })
      });
      const data = await res.json();
      if (data.success) {
        setCallState({ status: 'CONNECTED', sid: data.call_sid, phone: data.to });
        const greeting = "నమస్కారం అండి! I am calling from ElevateBox regarding your interest in building an e-commerce website. What kind of products are you planning to sell online?";
        setMessages([{ role: 'assistant', speaker: 'AI', text: greeting, language: 'Universal' }]);
      }
    } catch (err) {
      console.error('Failed to initiate Twilio call:', err);
      setCallState({ status: 'IDLE', sid: null, phone });
    }
  };

  // Start Interactive Web Voice Call (Universal)
  const handleStartWebCall = (phone) => {
    setCallState({ status: 'CONNECTED', sid: 'web_session', phone });
    setMessages([]);
    setMidCallFired(false);

    const initialGreeting = "నమస్కారం అండి! I am calling from ElevateBox regarding your interest in building an e-commerce website. What kind of products are you planning to sell online?";
    setMessages([{ role: 'assistant', speaker: 'AI', text: initialGreeting, language: 'Universal' }]);

    // Trigger TTS for greeting
    fetch('/api/calls/simulate-turn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        utterance: initialGreeting,
        phone_number: phone,
        history: []
      })
    }).then(r => r.json()).then(data => {
      if (data.audio_base64) playAudio(data.audio_base64);
    });
  };

  // End Call & Trigger Post-Call WhatsApp
  const handleEndCall = async () => {
    const phone = callState.phone || '8977155678';
    setCallState({ status: 'IDLE', sid: null, phone });
    setIsRecording(false);

    try {
      await fetch('/api/whatsapp/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phone,
          type: 'POST_CALL',
          lead_details: {
            ...qualification,
            intent: intentData.intent,
            caller_quotes: messages.filter(m => m.role === 'user').map(m => m.text).join(' | ') || "E-commerce store inquiry"
          }
        })
      });
      fetchWhatsAppLogs();
    } catch (e) {
      console.error('Failed to dispatch post-call WhatsApp:', e);
    }
  };

  // Send speech turn
  const handleSendMessage = async (userText) => {
    const updatedHistory = [...messages, { role: 'user', speaker: 'USER', text: userText }];
    setMessages(updatedHistory);

    try {
      const res = await fetch('/api/calls/simulate-turn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          utterance: userText,
          phone_number: callState.phone || '8977155678',
          history: updatedHistory.map(m => ({ role: m.role, content: m.text }))
        })
      });
      const data = await res.json();

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          speaker: 'AI',
          text: data.speech_response,
          language: data.language_detected,
          audioUrl: data.audio_base64
        }
      ]);

      handleTurnCompleted(data);
    } catch (err) {
      console.error('Error processing turn:', err);
    }
  };

  // Browser Web Speech Recognition
  const handleToggleRecord = () => {
    if (isRecording) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsRecording(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported on this browser. Please type in the text box below.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-IN';

    recognition.onstart = () => setIsRecording(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setIsRecording(false);
      handleSendMessage(transcript);
    };
    recognition.onerror = (e) => {
      console.error('Speech recognition error:', e);
      setIsRecording(false);
    };
    recognition.onend = () => setIsRecording(false);

    recognition.start();
  };

  // Quick Preset Test Scenarios across languages
  const handleRunSimulation = (scenario) => {
    handleStartWebCall('8977155678');
    setTimeout(() => {
      if (scenario === 'TANGLISH_HOT' || scenario === 'HOT_TELUGU') {
        handleSendMessage("Naku online saree business website kavali andi. Razorpay UPI undali, budget 40,000, next 2 weeks lo start cheyali. WhatsApp lo live demo pampandi.");
      } else if (scenario === 'HINGLISH_WARM' || scenario === 'WARM_HINDI') {
        handleSendMessage("Namaste, mujhe grocery store ke liye e-commerce website banwani hai, Razorpay integration chahiye, budget 35k hai. Kal subah 11 baje call back kijiye.");
      } else if (scenario === 'PURE_TELUGU') {
        handleSendMessage("నమస్కారం అండి, మా సూపర్ మార్కెట్ కి ఆన్‌లైన్ వెబ్‌సైట్ కావాలి, బడ్జెట్ 30,000, 2 వారాల్లో లాంచ్ చేయాలి. డెమో పంపించండి.");
      } else if (scenario === 'PURE_HINDI') {
        handleSendMessage("नमस्ते! हमें अपने रेडीमेड गारमेंट्स बिजनेस के लिए ऑनलाइन स्टोर चाहिए, 45,000 का बजट है, 10 दिन में लाइव करना है।");
      } else if (scenario === 'PURE_ENGLISH' || scenario === 'HOT_ENGLISH') {
        handleSendMessage("We need an urgent e-commerce store with 50 products, Shiprocket integration and ₹50,000 budget. Send live demo on WhatsApp immediately!");
      } else if (scenario === 'TAMIL_MIX') {
        handleSendMessage("Vanakkam! Engaluku online clothing business kaaga website venum, UPI payments integration oda, 40,000 budget. Live demo anupunga.");
      }
    }, 600);
  };

  const handleManualDispatch = async (type) => {
    try {
      await fetch('/api/whatsapp/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: config?.target_phone_number || '8977155678',
          type: type,
          lead_details: qualification
        })
      });
      fetchWhatsAppLogs();
      alert(`WhatsApp ${type} package successfully dispatched to ${config?.target_phone_number || '8977155678'}!`);
    } catch (e) {
      console.error('Manual dispatch error:', e);
    }
  };

  const handleSaveConfig = async (newConfig) => {
    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });
      fetchConfig();
    } catch (e) {
      console.error('Save config error:', e);
    }
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px 20px' }}>

      {/* Header */}
      <Header
        config={config}
        onOpenSettings={() => setIsConfigOpen(true)}
        isConnected={isConnected}
      />

      {/* Main Call Controller */}
      <CallControlPanel
        targetPhone={config?.target_phone_number || '8977155678'}
        onInitiateTwilioCall={handleInitiateTwilioCall}
        onStartWebCall={handleStartWebCall}
        onEndCall={handleEndCall}
        callState={callState}
        onRunSimulation={handleRunSimulation}
      />

      {/* Main Grid: Live Console & Intelligence Matrix */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(400px, 1.25fr) minmax(350px, 1fr)',
        gap: '24px',
        marginBottom: '24px'
      }}>
        {/* Left Column: Live Speech & Transcript Feed */}
        <LiveConsole
          messages={messages}
          onSendMessage={handleSendMessage}
          isRecording={isRecording}
          onToggleRecord={handleToggleRecord}
          midCallFired={midCallFired}
          isAudioPlaying={isAudioPlaying}
        />

        {/* Right Column: Lead Classification & Discovery Matrix */}
        <LeadMatrix
          intentData={intentData}
          qualification={qualification}
        />
      </div>

      {/* Bottom Grid: WhatsApp Cloud API Inspector & Scheduled Callbacks */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1.2fr 1fr',
        gap: '24px'
      }}>
        <WhatsAppFeed
          logs={whatsappLogs}
          onManualDispatch={handleManualDispatch}
          targetPhone={config?.target_phone_number || '8977155678'}
          candidatePhone={config?.candidate_phone || '8977155678'}
        />

        <CallbackList
          callbacks={callbacks}
        />
      </div>

      {/* Configuration & API Keys Modal */}
      <ConfigModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        config={config}
        onSaveConfig={handleSaveConfig}
      />

    </div>
  );
}
