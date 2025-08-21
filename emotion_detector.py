"""
Face Emotion Detection Module
Uses FER library with OpenCV for real-time face emotion detection
"""

import cv2
import numpy as np
from fer import FER

class FaceEmotionDetector:
    def __init__(self):
        """Initialize the face emotion detector"""
        self.detector = FER(mtcnn=True)  # Using MTCNN for better face detection
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
    def detect_emotion(self, frame):
        """
        Detect emotion from a video frame
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            tuple: (emotion_label, confidence, face_coordinates)
        """
        try:
            # Detect emotions
            result = self.detector.detect_emotions(frame)
            
            if result:
                # Get the first face (most prominent)
                face = result[0]
                emotion_scores = face['emotions']
                face_coords = face['box']
                
                # Find dominant emotion
                dominant_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = emotion_scores[dominant_emotion]
                
                return dominant_emotion, confidence, face_coords
            else:
                return None, 0.0, None
                
        except Exception as e:
            print(f"Face detection error: {e}")
            return None, 0.0, None
    
    def draw_results(self, frame, emotion, confidence, face_coords, stress_level, stress_score):
        """
        Draw emotion results on the frame with enhanced stress visualization
        
        Args:
            frame: OpenCV image frame
            emotion: detected emotion string
            confidence: confidence score
            face_coords: face bounding box coordinates
            stress_level: current stress level string
            stress_score: numeric stress score
        """
        # Get stress color
        stress_colors = {
            "RELAXED": (0, 255, 0),        # Bright Green
            "CALM": (0, 200, 100),         # Light Green
            "MILD STRESS": (0, 255, 255),  # Yellow
            "MODERATE STRESS": (0, 165, 255), # Orange
            "HIGH STRESS": (0, 0, 255)     # Red
        }
        color = stress_colors.get(stress_level, (128, 128, 128))
        
        if face_coords and emotion:
            # Draw face bounding box with stress-based color
            x, y, w, h = face_coords
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
            
            # Draw emotion label with confidence
            label = f"{emotion}: {confidence:.2f}"
            cv2.putText(frame, label, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw main stress level indicator (top-left)
        cv2.putText(frame, stress_level, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        
        # Draw stress score bar
        self._draw_stress_bar(frame, stress_score, color)
        
        return frame
    
    def _draw_stress_bar(self, frame, stress_score, color):
        """
        Draw a horizontal stress level bar
        
        Args:
            frame: OpenCV image frame
            stress_score: stress score (0-1)
            color: color for the bar
        """
        # Bar dimensions
        bar_x, bar_y = 10, 80
        bar_width, bar_height = 300, 20
        
        # Background bar (gray)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (64, 64, 64), -1)
        
        # Stress level bar (colored based on level)
        filled_width = int(bar_width * stress_score)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), color, -1)
        
        # Bar border
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        
        # Stress score text
        score_text = f"Stress Level: {stress_score:.2f}"
        cv2.putText(frame, score_text, (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Level markers
        markers = [0.25, 0.45, 0.65, 0.8]
        marker_labels = ["Calm", "Mild", "Mod", "High"]
        
        for i, (marker, label) in enumerate(zip(markers, marker_labels)):
            marker_x = bar_x + int(bar_width * marker)
            cv2.line(frame, (marker_x, bar_y), (marker_x, bar_y + bar_height), (255, 255, 255), 1)
            cv2.putText(frame, label, (marker_x - 15, bar_y + bar_height + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)