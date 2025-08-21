"""
Audio Test Script
Quick test to verify microphone is working and audio levels
"""

import sounddevice as sd
import numpy as np
import time

def test_audio():
    """Test audio input and show real-time levels"""
    print("=== Audio Test ===")
    
    # List available devices
    print("\nAvailable Audio Devices:")
    devices = sd.query_devices()
    input_devices = []
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append((i, device))
            print(f"  {i}: {device['name']} - {device['max_input_channels']} channels")
    
    if not input_devices:
        print("No input devices found!")
        return
    
    # Use default input device
    default_device = sd.default.device[0] if sd.default.device[0] is not None else input_devices[0][0]
    print(f"\nUsing device {default_device}: {sd.query_devices(default_device)['name']}")
    
    # Audio parameters
    sample_rate = 16000
    block_size = 1024
    
    # Real-time audio level monitoring
    print("\n=== Real-time Audio Monitoring ===")
    print("Speak into your microphone. You should see audio levels changing.")
    print("Press Ctrl+C to stop")
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Audio status: {status}")
        
        # Calculate audio level
        audio_level = np.sqrt(np.mean(indata ** 2))
        
        # Create visual level indicator
        level_bars = int(audio_level * 50)  # Scale to 50 bars max
        level_display = "█" * level_bars + "░" * (50 - level_bars)
        
        # Print level (overwrite previous line)
        print(f"\rAudio Level: {audio_level:.4f} |{level_display}|", end="", flush=True)
    
    try:
        # Start audio stream
        with sd.InputStream(
            device=default_device,
            samplerate=sample_rate,
            channels=1,
            callback=audio_callback,
            blocksize=block_size
        ):
            print("Listening... (Ctrl+C to stop)")
            while True:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n\nAudio test stopped.")
    except Exception as e:
        print(f"\nError during audio test: {e}")
        
        # Try with different settings
        print("Trying with default settings...")
        try:
            with sd.InputStream(callback=audio_callback):
                print("Listening with default settings...")
                time.sleep(5)
        except Exception as e2:
            print(f"Default settings also failed: {e2}")

def test_speech_detector():
    """Test the speech emotion detector directly"""
    print("\n=== Testing Speech Emotion Detector ===")
    
    try:
        from speech_detector import SpeechEmotionDetector
        
        detector = SpeechEmotionDetector()
        detector.start_recording()
        
        print("Speech detector started. Speak for 10 seconds...")
        
        for i in range(10):
            time.sleep(1)
            emotion, confidence = detector.get_current_emotion()
            print(f"Second {i+1}: {emotion} ({confidence:.2f})")
        
        detector.stop_recording()
        print("Speech detector test completed.")
        
    except ImportError:
        print("Could not import SpeechEmotionDetector. Make sure the module is available.")
    except Exception as e:
        print(f"Speech detector test failed: {e}")

if __name__ == "__main__":
    # Run basic audio test
    test_audio()
    
    # Test speech detector if user wants
    try:
        response = input("\nDo you want to test the speech emotion detector? (y/n): ")
        if response.lower() == 'y':
            test_speech_detector()
    except:
        pass