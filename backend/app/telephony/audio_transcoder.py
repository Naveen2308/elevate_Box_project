"""
Audio Transcoding Utilities for Twilio Media Streams <-> Gemini Multimodal Live API.

Twilio Media Streams:
- 8,000 Hz, 8-bit mono G.711 mu-law (PCMU)

Gemini Live API:
- Input: 16,000 Hz, 16-bit mono Little-Endian Linear PCM (mime_type="audio/pcm;rate=16000")
- Output: 24,000 Hz, 16-bit mono Little-Endian Linear PCM
"""

import numpy as np

# Standard ITU-T G.711 mu-law expansion table (8-bit mu-law -> 16-bit signed PCM)
MULAW_TO_PCM16_TABLE = np.zeros(256, dtype=np.int16)
for i in range(256):
    inv = ~i & 0xFF
    sign = inv & 0x80
    exponent = (inv >> 4) & 0x07
    mantissa = inv & 0x0F
    sample = ((mantissa << 3) + 0x84) << exponent
    sample -= 0x84
    MULAW_TO_PCM16_TABLE[i] = -sample if sign else sample

# Fast PCM16 to mu-law compression lookup table
def _build_pcm16_to_mulaw_table():
    pcm_vals = np.arange(-32768, 32768, dtype=np.int16)
    sign = (pcm_vals < 0).astype(np.uint8)
    mag = np.abs(pcm_vals).astype(np.int32)
    mag = np.clip(mag + 0x84, 0, 32767)
    
    exponent = np.zeros_like(mag, dtype=np.uint8)
    for exp in range(7, -1, -1):
        mask = (mag >= (0x84 << exp)) & (exponent == 0)
        exponent[mask] = exp
    
    mantissa = ((mag >> (exponent + 3)) & 0x0F).astype(np.uint8)
    ulaw_byte = ~( (sign << 7) | (exponent << 4) | mantissa ) & 0xFF
    return ulaw_byte.astype(np.uint8)

PCM16_TO_MULAW_TABLE = _build_pcm16_to_mulaw_table()


def mulaw_8k_to_pcm_16k(mulaw_bytes: bytes) -> bytes:
    """
    Decodes 8kHz 8-bit G.711 mu-law bytes from Twilio into 16kHz 16-bit Linear PCM for Gemini Live.
    Upsampling ratio: 2x (8kHz -> 16kHz) with linear interpolation.
    """
    if not mulaw_bytes:
        return b""

    u8_arr = np.frombuffer(mulaw_bytes, dtype=np.uint8)
    pcm_8k = MULAW_TO_PCM16_TABLE[u8_arr]
    
    n_in = len(pcm_8k)
    if n_in == 0:
        return b""
    
    x_in = np.arange(n_in)
    x_out = np.linspace(0, n_in - 1, n_in * 2)
    pcm_16k = np.interp(x_out, x_in, pcm_8k).astype(np.int16)
    
    return pcm_16k.tobytes()


def pcm_24k_to_mulaw_8k(pcm_24k_bytes: bytes) -> bytes:
    """
    Converts 24kHz 16-bit Linear PCM from Gemini Live into 8kHz 8-bit G.711 mu-law for Twilio.
    Downsampling ratio: 3:1 (24kHz -> 8kHz).
    """
    if not pcm_24k_bytes:
        return b""

    pcm_24k = np.frombuffer(pcm_24k_bytes, dtype=np.int16)
    if len(pcm_24k) == 0:
        return b""
    
    # 3:1 decimation
    pcm_8k = pcm_24k[::3]
    
    # Map int16 to index in lookup table (offset by +32768)
    table_indices = (pcm_8k.astype(np.int32) + 32768).astype(np.uint16)
    mulaw_8k = PCM16_TO_MULAW_TABLE[table_indices]
    
    return mulaw_8k.tobytes()
