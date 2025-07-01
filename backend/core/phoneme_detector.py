import os
import subprocess
import json
import tempfile
from pydub import AudioSegment

class PhonemeDetector:
    def __init__(self):
        # Path to Rhubarb executable (will need to be downloaded)
        self.rhubarb_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'rhubarb')
        
    def extract_phonemes(self, audio_path):
        """Extract phonemes from audio using Rhubarb Lip Sync"""
        
        # Convert to WAV if needed
        wav_path = self.ensure_wav_format(audio_path)
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            # Run Rhubarb
            cmd = [
                self.rhubarb_path,
                '-f', 'json',
                '-o', output_path,
                wav_path
            ]
            
            # For now, use a simple fallback if Rhubarb isn't available
            if not os.path.exists(self.rhubarb_path):
                print("Warning: Rhubarb not found, using simple phoneme generation")
                return self.generate_simple_phonemes(wav_path)
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Parse results
            with open(output_path, 'r') as f:
                data = json.load(f)
                # Rhubarb returns mouthCues with 'start' and 'value' fields
                # Convert to our expected format for both standard and canadian modes
                mouth_cues = data.get('mouthCues', [])
                
                # Add duration to each cue for better timing
                for i, cue in enumerate(mouth_cues):
                    if i < len(mouth_cues) - 1:
                        cue['duration'] = mouth_cues[i + 1]['start'] - cue['start']
                    else:
                        # Last cue gets a default duration
                        cue['duration'] = 0.2
                
                return mouth_cues
                
        except Exception as e:
            print(f"Rhubarb failed: {e}, using fallback")
            return self.generate_simple_phonemes(wav_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
            if wav_path != audio_path and os.path.exists(wav_path):
                os.unlink(wav_path)
    
    def ensure_wav_format(self, audio_path):
        """Convert audio to WAV format if needed"""
        if audio_path.lower().endswith('.wav'):
            return audio_path
        
        try:
            # Convert using pydub - it auto-detects format
            print(f"Converting {audio_path} to WAV format...")
            
            # Check if ffmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise Exception("ffmpeg not found. Please install it: brew install ffmpeg")
            
            audio = AudioSegment.from_file(audio_path)
            wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_path, format='wav')
            print(f"Converted to {wav_path}")
            return wav_path
        except Exception as e:
            if "ffmpeg" in str(e):
                raise
            print(f"Error converting audio: {e}")
            # Try with explicit format
            try:
                ext = audio_path.lower().split('.')[-1]
                audio = AudioSegment.from_file(audio_path, format=ext)
                wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_path, format='wav')
                return wav_path
            except Exception as e2:
                raise Exception(f"Failed to convert audio file. Make sure ffmpeg is installed: {e2}")
    
    def generate_simple_phonemes(self, audio_path):
        """Generate enhanced phoneme data with proper viseme codes for lip-sync"""
        import random
        
        audio = AudioSegment.from_wav(audio_path)
        duration = len(audio) / 1000.0  # Duration in seconds
        
        # Create enhanced phoneme pattern with Rhubarb viseme codes
        phonemes = []
        time = 0
        interval = 0.08  # 80ms intervals for more responsive animation
        
        # Viseme codes that create variety in mouth shapes
        viseme_options = {
            'silence': ['X'],  # Silence - closed mouth
            'soft': ['A', 'B'],  # Closed/small mouth sounds
            'medium': ['C', 'E', 'G'],  # Medium opening sounds  
            'loud': ['D', 'F', 'H']  # Wide opening sounds
        }
        
        prev_viseme = 'X'  # Start with silence
        
        while time < duration:
            # Get audio level at this point
            start_ms = int(time * 1000)
            end_ms = min(int((time + interval) * 1000), len(audio))
            
            if end_ms > start_ms:
                segment = audio[start_ms:end_ms]
                loudness = segment.dBFS
                
                # Map loudness to viseme category with more variety
                if loudness < -35:  # Quiet/silence
                    category = 'silence'
                elif loudness < -25:  # Soft speech
                    category = 'soft'
                elif loudness < -15:  # Medium speech
                    category = 'medium'
                else:  # Loud speech
                    category = 'loud'
                
                # Choose a viseme from the category, avoiding repetition
                available_visemes = viseme_options[category]
                if len(available_visemes) > 1 and prev_viseme in available_visemes:
                    # Try to pick a different viseme for variety
                    candidates = [v for v in available_visemes if v != prev_viseme]
                    if candidates:
                        available_visemes = candidates
                
                viseme = random.choice(available_visemes)
                prev_viseme = viseme
                
                # Add some random timing variation for more natural speech
                varied_time = time + random.uniform(-0.02, 0.02)
                varied_time = max(0, varied_time)  # Ensure time is not negative
                
                phonemes.append({
                    'start': varied_time,
                    'value': viseme,
                    'duration': interval + random.uniform(-0.02, 0.02)
                })
            
            time += interval
        
        # Sort by start time to ensure proper order
        phonemes.sort(key=lambda x: x['start'])
        
        print(f"Generated {len(phonemes)} viseme cues with variety:")
        viseme_counts = {}
        for p in phonemes:
            viseme_counts[p['value']] = viseme_counts.get(p['value'], 0) + 1
        print(f"Viseme distribution: {viseme_counts}")
        
        return phonemes
    
    def get_rhubarb_viseme_mapping(self):
        """Get mapping from Rhubarb viseme codes to sprite names"""
        return {
            'A': 'southparkClosed(M_B_P)',      # Closed mouth - M, B, P
            'B': 'southparkSmall(E_I)',         # Small opening - E, I  
            'C': 'southparkMedium(E_EH)',       # Medium opening - E, EH
            'D': 'southparkWide(A_AH)',         # Wide opening - A, AH
            'E': 'southparkRound(O_OO)',        # Round shape - O, OO
            'F': 'southparkTeeth(F_V)',         # Teeth showing - F, V
            'G': 'southparkSpecial(L_TH_R)',    # Special consonants - L, TH, R
            'H': 'southparkWide(A_AH)',         # Other vowels (use wide)
            'X': 'southparkClosed(M_B_P)'       # Silence (use closed)
        }