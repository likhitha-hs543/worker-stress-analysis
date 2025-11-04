"""
Speech Emotion Detection Test
Test the simplified and accurate speech detection system
"""

import time
from speech_detector import SpeechEmotionDetector

def test_speech_detection():
    """Test speech emotion detection"""
    print("\n"*2)
    print("="*70)
    print(" "*15 + "SPEECH EMOTION DETECTION TEST")
    print("="*70)
    print()
    print("🎯 TESTING INSTRUCTIONS:")
    print("-" * 70)
    print()
    print("  ⏱️  First 3 seconds: STAY QUIET (calibration)")
    print()
    print("  Then test these emotions (speak for 3-4 seconds each):")
    print()
    print("  1. 🗣️  NEUTRAL: Speak normally like you're having a conversation")
    print("  2. 😠 ANGRY: Speak LOUDLY and FORCEFULLY (like you're yelling)")
    print("  3. 😊 HAPPY: Speak with ENERGY and EXCITEMENT (upbeat tone)")
    print("  4. 😢 SAD: Speak QUIETLY and SLOWLY (low energy, monotone)")
    print("  5. 🔇 SILENCE: Stop speaking for 5 seconds")
    print()
    print("  💡 Tips for better detection:")
    print("     - Exaggerate your emotions")
    print("     - Speak for at least 2-3 seconds continuously")
    print("     - Use VERY different voice characteristics")
    print()
    print("  Press Ctrl+C to stop the test")
    print("-" * 70)
    print()
    
    # Initialize detector
    detector = SpeechEmotionDetector()
    
    # Start recording
    detector.start_recording()
    
    try:
        test_duration = 60  # 60 second test
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
            time.sleep(1)
        
        print("\n✅ Test completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test stopped by user")
    
    finally:
        # Show final statistics
        print("\n" + "="*70)
        print(" "*25 + "FINAL STATISTICS")
        print("="*70)
        stats = detector.get_statistics()
        print(f"  Total chunks processed:  {stats['total_chunks']}")
        print(f"  Speech chunks detected:  {stats['speech_chunks']}")
        print(f"  Speech activity:         {stats['speech_ratio']:.1%}")
        print(f"  Calibrated:              {stats['calibrated']}")
        print(f"  Energy threshold:        {stats['threshold']:.4f}")
        print()
        print("  Emotion detections:")
        for emotion, count in stats['emotion_counts'].items():
            if count > 0:
                print(f"    {emotion.capitalize():10s}: {count} times")
        print("="*70)
        
        # Stop detector
        detector.stop_recording()

if __name__ == "__main__":
    test_speech_detection()

