"""
Test Enhanced Accuracy System
Validates DeepFace integration and context-aware analysis
"""

import cv2
import time
from emotion_detector import FaceEmotionDetector
from stress_analyzer import StressAnalyzer

def test_enhanced_system():
    """Test the enhanced accuracy system"""
    print("Testing Enhanced Accuracy System")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing DeepFace detector...")
    detector = FaceEmotionDetector(
        backend='opencv',  # Fast for testing
        model_name='Facenet512',
        enable_smoothing=True
    )
    
    print("\n2. Initializing enhanced stress analyzer...")
    analyzer = StressAnalyzer(
        history_size=15,
        enable_context=True
    )
    
    print("\n3. Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open webcam")
        return
    
    print("\nSystem ready! Testing for 30 seconds...")
    print("   • Press Q to quit early")
    print("   • Press S to show statistics")
    print("")
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 30:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame_count += 1
        
        # Detect emotion (process every 3rd frame for speed)
        if frame_count % 3 == 0:
            emotion, confidence, face_coords = detector.detect_emotion(frame)
            
            if emotion:
                # Analyze stress (using neutral for speech in this test)
                stress_level, stress_score, details = analyzer.analyze_stress(
                    emotion, confidence,
                    'neutral', 0.5
                )
                
                # Draw results
                frame = detector.draw_results(
                    frame, emotion, confidence, face_coords,
                    stress_level, stress_score
                )
        
        # Display
        cv2.imshow('Enhanced Accuracy Test', frame)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            stats = detector.get_statistics()
            print(f"\nCurrent Statistics:")
            print(f"   Success Rate: {stats['success_rate']:.1%}")
            print(f"   Avg Processing: {stats['avg_processing_time_ms']:.1f}ms")
            print(f"   Current Emotion: {stats['current_emotion']} ({stats['current_confidence']:.1%})")
    
    # Final statistics
    print("\nFinal Test Results:")
    stats = detector.get_statistics()
    stress_stats = analyzer.get_stress_statistics()
    
    print(f"\n   Detection Performance:")
    print(f"      Total Frames: {stats['total_detections']}")
    print(f"      Success Rate: {stats['success_rate']:.1%}")
    print(f"      Avg Processing: {stats['avg_processing_time_ms']:.1f}ms")
    
    print(f"\n   Stress Analysis:")
    print(f"      Average Stress: {stress_stats['average_stress']:.2f}")
    print(f"      Current Level: {stress_stats['current_level']}")
    print(f"      Pattern: {stress_stats['pattern']}")
    print(f"      Overall Confidence: {stress_stats['confidence']:.1%}")
    
    print(f"\n   Context Info:")
    if 'context' in stress_stats:
        ctx = stress_stats['context']
        print(f"      Session Duration: {ctx['session_duration_min']:.1f} min")
        print(f"      Time of Day: {ctx['time_of_day']}")
        print(f"      Stress Events: {ctx['stress_events_last_hour']}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\nTest completed successfully!")
    print("\nObservations:")
    if stats['success_rate'] > 0.85:
        print("   Excellent detection rate (>85%)")
    elif stats['success_rate'] > 0.70:
        print("   Good detection rate, but could be better")
    else:
        print("   Low detection rate - check lighting and camera")
    
    if stats['avg_processing_time_ms'] < 100:
        print("   Excellent performance (<100ms)")
    elif stats['avg_processing_time_ms'] < 200:
        print("   Acceptable performance, but consider optimization")
    else:
        print("   Slow performance - consider using 'opencv' backend")

if __name__ == "__main__":
    test_enhanced_system()
