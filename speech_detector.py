"""
Speech Emotion Detection Module
Uses SpeechBrain pretrained model for real-time speech emotion recognition
"""

import numpy as np
import sounddevice as sd
import threading
import queue
import torch
import torchaudio
from speechbrain.pretrained import EncoderClassifier
import tempfile
import os
import time
import librosa

class SpeechEmotionDetector:
    def __init__(self, sample_rate=16000, chunk_duration=2.0):
        """
        Initialize speech emotion detector
        
        Args:
            sample_rate: Audio sample rate
            chunk_duration: Duration of audio chunks to analyze (seconds)
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_samples = int(sample_rate * chunk_duration)
        
        # Audio buffer and threading
        self.audio_buffer = []
        self.is_recording = False
        self.current_emotion = "neutral"
        self.emotion_confidence = 0.0
        self.last_update_time = time.time()
        
        # Audio stream settings
        self.blocksize = 1024
        self.device = None  # Use default device
        
        # Load pretrained model
        print("Loading speech emotion model...")
        try:
            self.classifier = EncoderClassifier.from_hparams(
                source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
                savedir="pretrained_models/emotion_recognition"
            )
            print("Speech emotion model loaded successfully")
        except Exception as e:
            print(f"Error loading speech model: {e}")
            print("Falling back to simple volume-based detection...")
            self.classifier = None
            
        # Emotion mapping to match our stress categories
        self.emotion_mapping = {
            'neu': 'neutral',
            'hap': 'happy', 
            'sad': 'sad',
            'ang': 'angry',
            'fea': 'fear',
            'dis': 'disgust',
            'sur': 'surprise'
        }
        
        # Simple fallback emotions based on audio characteristics
        self.fallback_emotions = ['neutral', 'happy', 'sad', 'angry']
        self.emotion_cycle_counter = 0
    
    def audio_callback(self, indata, frames, time, status):
        """Callback function for audio input"""
        if status:
            print(f"Audio input status: {status}")
        
        # Add audio data to buffer
        if self.is_recording:
            # Convert to mono and flatten
            audio_data = indata.flatten() if indata.ndim > 1 else indata
            self.audio_buffer.extend(audio_data)
            
            # Keep buffer size manageable (10 seconds max)
            max_buffer_size = self.sample_rate * 10
            if len(self.audio_buffer) > max_buffer_size:
                self.audio_buffer = self.audio_buffer[-max_buffer_size:]
    
    def start_recording(self):
        """Start audio recording in a separate thread"""
        print("Starting audio recording...")
        
        # List available audio devices for debugging
        try:
            devices = sd.query_devices()
            print("Available audio devices:")
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    print(f"  {i}: {device['name']} (input)")
        except Exception as e:
            print(f"Error listing devices: {e}")
        
        self.is_recording = True
        self.audio_buffer = []
        
        try:
            # Start audio stream
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
            self.processing_thread = threading.Thread(target=self._process_audio)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            print("Speech emotion detection started successfully")
            
        except Exception as e:
            print(f"Error starting audio recording: {e}")
            print("Speech detection will use fallback mode")
            self.is_recording = False
    
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
    
    def _process_audio(self):
        """Process audio chunks for emotion detection"""
        print("Audio processing thread started")
        
        while self.is_recording:
            try:
                # Wait for enough audio data
                if len(self.audio_buffer) >= self.chunk_samples:
                    # Get audio chunk
                    audio_chunk = np.array(self.audio_buffer[-self.chunk_samples:])
                    
                    # Check if there's actual audio activity
                    audio_energy = np.sqrt(np.mean(audio_chunk ** 2))
                    print(f"Audio energy: {audio_energy:.4f}")  # Debug output
                    
                    if audio_energy > 0.01:  # Voice activity threshold
                        # Detect emotion
                        emotion, confidence = self._detect_emotion_from_audio(audio_chunk)
                        
                        if emotion:
                            self.current_emotion = emotion
                            self.emotion_confidence = confidence
                            self.last_update_time = time.time()
                            print(f"Speech Emotion Updated: {emotion} ({confidence:.2f})")
                    else:
                        # No significant audio, check if we should reset to neutral
                        if time.time() - self.last_update_time > 5.0:  # 5 seconds of silence
                            self.current_emotion = "neutral"
                            self.emotion_confidence = 0.5
                            print("Speech: Silence detected, defaulting to neutral")
                
                time.sleep(0.5)  # Process every 500ms
                
            except Exception as e:
                print(f"Audio processing error: {e}")
                time.sleep(1)
    
    def _detect_emotion_from_audio(self, audio_data):
        """
        Detect emotion from audio data with fallback methods
        
        Args:
            audio_data: numpy array of audio samples
            
        Returns:
            tuple: (emotion_label, confidence)
        """
        # Method 1: Try SpeechBrain model if available
        if self.classifier is not None:
            try:
                return self._speechbrain_detection(audio_data)
            except Exception as e:
                print(f"SpeechBrain detection failed: {e}")
                # Fall through to backup method
        
        # Method 2: Simple audio feature-based detection (fallback)
        return self._simple_audio_detection(audio_data)
    
    def _speechbrain_detection(self, audio_data):
        """Use SpeechBrain model for detection"""
        # Ensure proper audio format
        audio_tensor = torch.FloatTensor(audio_data).unsqueeze(0)
        
        # Normalize audio
        if torch.max(torch.abs(audio_tensor)) > 0:
            audio_tensor = audio_tensor / torch.max(torch.abs(audio_tensor))
        
        # Get prediction
        out_prob, score, index, text_lab = self.classifier.classify_batch(audio_tensor)
        
        # Extract emotion
        predicted_emotion = text_lab[0]
        confidence = torch.max(out_prob).item()
        
        # Map to our emotion categories
        emotion = self.emotion_mapping.get(predicted_emotion, predicted_emotion)
        
        return emotion, confidence
    
    def _simple_audio_detection(self, audio_data):
        """Simple fallback detection based on audio features"""
        try:
            # Calculate basic audio features
            energy = np.sqrt(np.mean(audio_data ** 2))
            zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
            spectral_centroid = self._calculate_spectral_centroid(audio_data)
            
            # Simple rule-based classification
            if energy > 0.15:  # High energy
                if zero_crossings > len(audio_data) * 0.1:
                    emotion = "angry"
                    confidence = min(energy * 2, 0.8)
                else:
                    emotion = "happy" 
                    confidence = min(energy * 1.5, 0.7)
            elif energy > 0.05:  # Medium energy
                if spectral_centroid < 0.3:
                    emotion = "sad"
                    confidence = 0.6
                else:
                    emotion = "neutral"
                    confidence = 0.5
            else:  # Low energy
                emotion = "neutral"
                confidence = 0.4
            
            return emotion, confidence
            
        except Exception as e:
            print(f"Simple detection error: {e}")
            # Absolute fallback - cycle through emotions for testing
            self.emotion_cycle_counter += 1
            emotion = self.fallback_emotions[self.emotion_cycle_counter % len(self.fallback_emotions)]
            return emotion, 0.3
    
    def _calculate_spectral_centroid(self, audio_data):
        """Calculate spectral centroid as a simple audio feature"""
        try:
            # Simple FFT-based spectral centroid
            fft = np.abs(np.fft.fft(audio_data))
            freqs = np.fft.fftfreq(len(fft))
            
            # Calculate centroid
            centroid = np.sum(freqs * fft) / np.sum(fft) if np.sum(fft) > 0 else 0
            return abs(centroid)
        except:
            return 0.5
    
    def get_current_emotion(self):
        """Get the current detected emotion"""
        return self.current_emotion, self.emotion_confidence