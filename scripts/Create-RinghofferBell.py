"""Generate an original, short tram bell sample using only Python's standard library."""
import math
import struct
import wave
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / 'Assets/MoreScrapItems/Audio/Ringhoffer240Bell.wav'
out.parent.mkdir(parents=True, exist_ok=True)
rate = 44100
duration = 1.25
samples = []
for i in range(int(rate * duration)):
    t = i / rate
    signal = 0.0
    for onset, gain in ((0.0, .62), (.21, .37)):
        age = t - onset
        if age < 0:
            continue
        envelope = (1 - math.exp(-age * 950)) * math.exp(-age * 5.2)
        # An inharmonic metallic bell with a second quick strike.
        partials = ((1.0, 1210, 0), (.43, 2417, .35), (.21, 3263, 1.2), (.12, 4765, .7))
        signal += gain * envelope * sum(a * math.sin(2 * math.pi * f * age + phase)
                                         for a, f, phase in partials)
    samples.append(max(-1, min(1, signal * .62)))
with wave.open(str(out), 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(rate)
    wav.writeframes(struct.pack('<%dh' % len(samples), *(int(s * 32767) for s in samples)))
print(out)
