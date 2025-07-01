import numpy as np
import wave

# Generate a simple test audio file with varying tones
sample_rate = 44100
duration = 5  # seconds

# Create audio data with varying frequencies to simulate speech
t = np.linspace(0, duration, int(sample_rate * duration))
audio_data = np.zeros_like(t)

# Add different frequency components to simulate speech patterns
for i in range(0, len(t), sample_rate // 2):
    end = min(i + sample_rate // 2, len(t))
    freq = np.random.randint(100, 400)  # Random frequency between 100-400 Hz
    amplitude = np.random.uniform(0.3, 1.0)
    audio_data[i:end] += amplitude * np.sin(2 * np.pi * freq * t[i:end])

# Add some silence periods
for i in range(0, len(t), sample_rate * 2):
    silence_start = i + int(sample_rate * 0.8)
    silence_end = min(silence_start + int(sample_rate * 0.2), len(t))
    audio_data[silence_start:silence_end] *= 0.1

# Normalize
audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

# Save as WAV file
with wave.open('test_audio.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)   # 16-bit
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())

print("Created test_audio.wav (5 seconds)")