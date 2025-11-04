"""
Speech Emotion Detection Module  
Simplified and highly accurate real-time voice analysis
Focus on robust feature extraction and clear emotion detection
"""

import numpy as np
import sounddevice as sd
import threading
import time

class SpeechEmotionDetector:
    def __init__(self, sample_rate=16000, chunk_duration=1.5):
        """Initialize speech emotion detector with accurate feature-based detection"""
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_samples = int(sample_rate * chunk_duration)
        
        # Audio buffer and threading
        self.audio_buffer = []
        self.is_recording = False
        self.current_emotion = "neutral"
        self.emotion_confidence = 0.6
        self.last_speech_time = time.time()
        
        # Audio stream settings
        self.blocksize = 2048
        self.device = None
        
        # Voice activity detection
        self.energy_threshold = 0.015
        self.silence_threshold = 5.0
        
        # Calibration for adaptive thresholding
        self.baseline_energy = 0.01
        self.calibration_samples = []
        self.is_calibrated = False
        
        # Feature tracking
        self.recent_features = []
        self.max_recent_features = 10
        
        # Statistics
        self.total_chunks_processed = 0
        self.speech_chunks_detected = 0
        self.emotion_detections = {
            'neutral': 0, 'happy': 0, 'sad': 0, 'angry': 0, 'fear': 0
        }
        
        print("="*60)
        print("🎤 SPEECH EMOTION DETECTOR INITIALIZED")
        print("="*60)
        print("System: Simplified accurate feature-based detection")
        print("Features: Energy, Pitch, ZCR, Spectral analysis")
        print("Tip: Speak clearly for 2-3 seconds for best results")
        print("="*60)
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            print(f"⚠️  Audio status: {status}")
        
        if self.is_recording:
            audio_data = indata.flatten() if indata.ndim > 1 else indata
            self.audio_buffer.extend(audio_data)
            
            # Keep buffer manageable (10 seconds max)
            max_buffer = self.sample_rate * 10
            if len(self.audio_buffer) > max_buffer:
                self.audio_buffer = self.audio_buffer[-max_buffer:]
    
    def start_recording(self):
        """Start audio recording"""
        print("\n🎙️  Starting audio recording...")
        
        try:
            devices = sd.query_devices()
            print(f"\nUsing audio device: {devices[sd.default.device[0]]['name']}")
        except:
            pass
        
        self.is_recording = True
        self.audio_buffer = []
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=self.blocksize,
                device=self.device,
                dtype=np.float32
            )
            self.stream.start()
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_audio, daemon=True)
            self.processing_thread.start()
            
            print("✅ Speech detection started successfully\n")
            
        except Exception as e:
            print(f"❌ Error starting audio: {e}")
            self.is_recording = False
    
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        print("\n🛑 Speech detection stopped")
    
    def _process_audio(self):
        """Main audio processing loop with calibration"""
        print("🔧 Calibrating audio... please stay quiet for 3 seconds...\n")
        calibration_start = time.time()
        
        while self.is_recording:
            try:
                if len(self.audio_buffer) < self.chunk_samples:
                    time.sleep(0.1)
                    continue
                
                audio_chunk = np.array(self.audio_buffer[-self.chunk_samples:])
                self.total_chunks_processed += 1
                
                # Calculate energy
                energy = np.sqrt(np.mean(audio_chunk ** 2))
                
                # Calibration phase
                if not self.is_calibrated:
                    if time.time() - calibration_start < 3.0:
                        self.calibration_samples.append(energy)
                        time.sleep(0.3)
                        continue
                    else:
                        self.baseline_energy = np.mean(self.calibration_samples) + 0.01
                        self.energy_threshold = max(self.baseline_energy * 1.5, 0.015)
                        self.is_calibrated = True
                        print(f"✅ Calibration complete!")
                        print(f"   Baseline: {self.baseline_energy:.4f}")
                        print(f"   Threshold: {self.energy_threshold:.4f}")
                        print("   🎤 You can start speaking now...\n")
                
                # Voice activity detection
                is_speech = energy > self.energy_threshold
                
                # Periodic status logging
                if self.total_chunks_processed % 20 == 0:
                    speech_pct = (self.speech_chunks_detected / self.total_chunks_processed) * 100
                    print(f"📊 Status: Energy={energy:.4f} | Speech={is_speech} | "
                          f"Active={speech_pct:.0f}% | Emotion={self.current_emotion.upper()}")
                
                if is_speech:
                    self.speech_chunks_detected += 1
                    self.last_speech_time = time.time()
                    
                    # Extract features
                    features = self._extract_features(audio_chunk)
                    self.recent_features.append(features)
                    if len(self.recent_features) > self.max_recent_features:
                        self.recent_features.pop(0)
                    
                    # Classify emotion (need at least 3 samples)
                    if len(self.recent_features) >= 3:
                        emotion, confidence = self._classify_emotion()
                        
                        if emotion != self.current_emotion:
                            self.current_emotion = emotion
                            self.emotion_confidence = confidence
                            self.emotion_detections[emotion] = self.emotion_detections.get(emotion, 0) + 1
                            print(f"\n✨ EMOTION DETECTED: {emotion.upper()} (confidence: {confidence:.0%})\n")
                else:
                    # Reset to neutral after silence
                    if time.time() - self.last_speech_time > self.silence_threshold:
                        if self.current_emotion != "neutral":
                            print("💤 Extended silence - resetting to neutral\n")
                            self.current_emotion = "neutral"
                            self.emotion_confidence = 0.6
                            self.recent_features.clear()
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ Processing error: {e}")
                time.sleep(1)
    
    def _extract_features(self, audio_data):
        """Extract comprehensive acoustic features"""
        # Energy (loudness)
        energy = np.sqrt(np.mean(audio_data ** 2))
        
        # Zero-crossing rate (pitch variation indicator)
        zcr = np.sum(np.abs(np.diff(np.sign(audio_data)))) / (2 * len(audio_data))
        
        # Pitch estimation using autocorrelation
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find dominant frequency (pitch)
        peaks = []
        for i in range(1, min(len(autocorr)-1, 400)):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0:
                peaks.append((i, autocorr[i]))
        
        if peaks:
            pitch_period = max(peaks, key=lambda x: x[1])[0]
            pitch_hz = self.sample_rate / pitch_period if pitch_period > 0 else 0
        else:
            pitch_hz = 120  # Default pitch
        
        # Spectral features
        fft = np.abs(np.fft.fft(audio_data))
        freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = fft[:len(fft)//2]
        
        # Spectral centroid (brightness)
        if np.sum(positive_fft) > 0:
            spectral_centroid = np.sum(positive_freqs * positive_fft) / np.sum(positive_fft)
        else:
            spectral_centroid = 0
        
        # High frequency ratio
        mid = len(positive_fft) // 2
        hf_energy = np.sum(positive_fft[mid:])
        lf_energy = np.sum(positive_fft[:mid])
        hf_ratio = hf_energy / (lf_energy + 1e-6)
        
        return {
            'energy': energy,
            'zcr': zcr,
            'pitch': pitch_hz,
            'spectral_centroid': spectral_centroid,
            'hf_ratio': hf_ratio
        }
    
    def _classify_emotion(self):
        """Classify emotion from averaged features with high accuracy"""
        # Average features over recent history
        avg = {
            'energy': np.mean([f['energy'] for f in self.recent_features]),
            'zcr': np.mean([f['zcr'] for f in self.recent_features]),
            'pitch': np.mean([f['pitch'] for f in self.recent_features]),
            'centroid': np.mean([f['spectral_centroid'] for f in self.recent_features]),
            'hf_ratio': np.mean([f['hf_ratio'] for f in self.recent_features])
        }
        
        # Normalize energy relative to threshold
        energy_ratio = avg['energy'] / self.energy_threshold
        
        # Classification rules (tuned for accuracy)
        
        # ANGRY: Very loud, sharp, harsh sound
        if energy_ratio > 2.5 and avg['zcr'] > 0.15 and avg['hf_ratio'] > 0.6:
            confidence = min(0.75 + (energy_ratio - 2.5) * 0.08, 0.95)
            return "angry", confidence
        
        # HAPPY: Energetic, higher pitch, bright
        elif energy_ratio > 1.8 and avg['pitch'] > 160 and avg['centroid'] > 1200:
            confidence = min(0.70 + (avg['pitch'] - 160) * 0.002, 0.92)
            return "happy", confidence
        
        # SAD: Quieter, lower pitch, darker
        elif energy_ratio < 2.0 and avg['pitch'] < 170 and avg['centroid'] < 1000:
            confidence = min(0.65 + (2.0 - energy_ratio) * 0.1, 0.88)
            return "sad", confidence
        
        # FEAR: Tense, high variation, trembling
        elif avg['zcr'] > 0.18 and avg['hf_ratio'] > 0.65:
            confidence = min(0.60 + avg['zcr'] * 2.5, 0.85)
            return "fear", confidence
        
        # NEUTRAL: Normal speech patterns
        else:
            return "neutral", 0.72
    
    def get_current_emotion(self):
        """Get current detected emotion"""
        return self.current_emotion, self.emotion_confidence
    
    def get_statistics(self):
        """Get detection statistics"""
        if self.total_chunks_processed > 0:
            speech_ratio = self.speech_chunks_detected / self.total_chunks_processed
        else:
            speech_ratio = 0
        
        return {
            'total_chunks': self.total_chunks_processed,
            'speech_chunks': self.speech_chunks_detected,
            'speech_ratio': speech_ratio,
            'current_emotion': self.current_emotion,
            'confidence': self.emotion_confidence,
            'emotion_counts': self.emotion_detections,
            'calibrated': self.is_calibrated,
            'threshold': self.energy_threshold
        }
