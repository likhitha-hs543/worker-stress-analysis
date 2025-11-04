"""
Main Application: Worker Stress Analysis
Real-time face and speech emotion detection for stress analysis
"""

import cv2
import time
import sys
import threading
from emotion_detector import FaceEmotionDetector
from speech_detector import SpeechEmotionDetector  
from stress_analyzer import StressAnalyzer

class WorkerStressAnalysis:
    def __init__(self):
        """Initialize the stress analysis system"""
        print("Initializing Worker Stress Analysis System...")
        
        # Initialize components
        self.face_detector = FaceEmotionDetector()
        self.speech_detector = SpeechEmotionDetector()
        self.stress_analyzer = StressAnalyzer()
        
        # Video capture
        self.cap = None
        self.is_running = False
        
        # Current states
        self.current_face_emotion = "neutral"
        self.current_face_confidence = 0.0
        self.current_speech_emotion = "neutral"
        self.current_speech_confidence = 0.0
        self.current_stress_level = "CALM"
        self.current_stress_score = 0.0
        
        # For real-time updates and smoothing
        self.last_update_time = time.time()
        self.update_interval = 0.5  # Update every 500ms for smooth real-time feel
        
        print("System initialized successfully!")
    
    def start_system(self):
        """Start the complete stress analysis system"""
        try:
            # Initialize video capture
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not access webcam")
                return False
            
            # Set video properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 15)
            
            # Start speech detection
            self.speech_detector.start_recording()
            
            self.is_running = True
            print("\n=== Worker Stress Analysis Started ===")
            print("Instructions:")
            print("- Look at the camera and speak naturally")
            print("- Stress levels: RELAXED → CALM → MILD → MODERATE → HIGH")
            print("- Real-time updates every 500ms")
            print("- Press 'q' to quit, 's' for statistics, 'r' to reset")
            print("========================================\n")
            
            # Start main processing loop
            self._main_processing_loop()
            
            return True
            
        except Exception as e:
            print(f"Error starting system: {e}")
            return False
    
    def _main_processing_loop(self):
        """Main processing loop for real-time analysis"""
        frame_count = 0
        fps_counter = 0
        fps_start_time = time.time()
        
        while self.is_running:
            try:
                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                frame_count += 1
                
                # Process face emotion (every few frames for performance)
                if frame_count % 3 == 0:  # Process every 3rd frame
                    face_emotion, face_conf, face_coords = self.face_detector.detect_emotion(frame)
                    if face_emotion:
                        self.current_face_emotion = face_emotion
                        self.current_face_confidence = face_conf
                
                # Get current speech emotion
                speech_emotion, speech_conf = self.speech_detector.get_current_emotion()
                self.current_speech_emotion = speech_emotion
                self.current_speech_confidence = speech_conf
                
                # Real-time stress analysis with smooth updates
                current_time = time.time()
                if current_time - self.last_update_time >= self.update_interval:
                    # Analyze stress
                    stress_level, stress_score, details = self.stress_analyzer.analyze_stress(
                        self.current_face_emotion,
                        self.current_face_confidence,
                        self.current_speech_emotion,
                        self.current_speech_confidence
                    )
                    
                    self.current_stress_level = stress_level
                    self.current_stress_score = stress_score
                    self.last_update_time = current_time
                
                # Draw results on frame
                frame = self._draw_comprehensive_results(frame)
                
                # Display frame
                cv2.imshow('Worker Stress Analysis', frame)
                
                # Calculate and display FPS with real-time updates
                fps_counter += 1
                if fps_counter % 15 == 0:  # Update console every 15 frames for real-time feel
                    fps_end_time = time.time()
                    fps = 15 / (fps_end_time - fps_start_time)
                    print(f"FPS: {fps:.1f} | Face: {self.current_face_emotion} | Speech: {self.current_speech_emotion} | Level: {self.current_stress_level}")
                    fps_start_time = fps_end_time
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._show_statistics()
                elif key == ord('r'):
                    self.stress_analyzer.reset_history()
                    print("History reset!")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Processing error: {e}")
                continue
    
    def _draw_comprehensive_results(self, frame):
        """Draw comprehensive analysis results on frame with real-time updates"""
        # Get face coordinates from the detector
        _, _, face_coords = self.face_detector.detect_emotion(frame)
        
        # Draw face emotion results with new stress level system
        frame = self.face_detector.draw_results(
            frame, 
            self.current_face_emotion,
            self.current_face_confidence,
            face_coords,
            self.current_stress_level,
            self.current_stress_score
        )
        
        # Add speech emotion info with enhanced styling
        speech_text = f"Speech: {self.current_speech_emotion} ({self.current_speech_confidence:.2f})"
        cv2.putText(frame, speech_text, (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add real-time timestamp
        current_time = time.strftime("%H:%M:%S")
        cv2.putText(frame, f"Time: {current_time}", (frame.shape[1] - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add trend indicator if available
        stats = self.stress_analyzer.get_stress_statistics()
        if stats['total_samples'] > 5:
            trend = stats['trend']
            trend_color = (0, 255, 255) if trend == 'increasing' else (0, 255, 0) if trend == 'decreasing' else (255, 255, 255)
            cv2.putText(frame, f"Trend: {trend}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, trend_color, 2)
        
        # Add instructions
        cv2.putText(frame, "Q:Quit | S:Stats | R:Reset", 
                   (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def _show_statistics(self):
        """Display comprehensive stress analysis statistics"""
        stats = self.stress_analyzer.get_stress_statistics()
        print("\n" + "="*50)
        print("          STRESS ANALYSIS STATISTICS")
        print("="*50)
        print(f"Current Stress Level: {self.current_stress_level}")
        print(f"Current Score: {self.current_stress_score:.3f}")
        print(f"Average Stress: {stats['average_stress']:.3f}")
        print(f"Trend: {stats['trend'].upper()}")
        print(f"Total Samples: {stats['total_samples']}")
        print(f"Max Stress: {stats['max_stress']:.3f}")
        print(f"Min Stress: {stats['min_stress']:.3f}")
        
        print("\nStress Level Distribution:")
        for level, count in stats['stress_distribution'].items():
            percentage = (count / max(stats['total_samples'], 1)) * 100
            bar = "█" * int(percentage / 5)  # Visual bar
            print(f"  {level:15}: {count:3d} ({percentage:5.1f}%) {bar}")
        
        print("\nCurrent Emotion Details:")
        print(f"  Face Emotion: {self.current_face_emotion} (conf: {self.current_face_confidence:.2f})")
        print(f"  Speech Emotion: {self.current_speech_emotion} (conf: {self.current_speech_confidence:.2f})")
        print("="*50 + "\n")
    
    def stop_system(self):
        """Stop the stress analysis system"""
        print("\nStopping Worker Stress Analysis System...")
        
        self.is_running = False
        
        # Stop speech detection
        if hasattr(self, 'speech_detector'):
            self.speech_detector.stop_recording()
        
        # Release video capture
        if self.cap:
            self.cap.release()
        
        # Close windows
        cv2.destroyAllWindows()
        
        print("System stopped successfully!")

def main():
    """Main function"""
    # Create and start the system
    stress_system = WorkerStressAnalysis()
    
    try:
        success = stress_system.start_system()
        if not success:
            print("Failed to start system")
            return
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        stress_system.stop_system()

if __name__ == "__main__":
    main()