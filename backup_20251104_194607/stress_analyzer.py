"""
Stress Analysis Module
Combines face and speech emotions to determine stress level
"""

import time
from collections import deque

class StressAnalyzer:
    def __init__(self, history_size=10):
        """
        Initialize stress analyzer
        
        Args:
            history_size: Number of recent predictions to consider for smoothing
        """
        self.history_size = history_size
        self.face_emotion_history = deque(maxlen=history_size)
        self.speech_emotion_history = deque(maxlen=history_size)
        self.stress_history = deque(maxlen=history_size)
        
        # Define stress-indicating emotions
        self.stress_emotions = {'angry', 'sad', 'fear', 'disgust'}
        self.neutral_emotions = {'neutral', 'happy', 'surprise'}
        
        # Weights for different modalities
        self.face_weight = 0.6
        self.speech_weight = 0.4
        
    def analyze_stress(self, face_emotion, face_confidence, speech_emotion, speech_confidence):
        """
        Analyze stress level based on face and speech emotions
        
        Args:
            face_emotion: detected face emotion
            face_confidence: confidence of face emotion
            speech_emotion: detected speech emotion  
            speech_confidence: confidence of speech emotion
            
        Returns:
            tuple: (stress_level, stress_score, analysis_details)
        """
        # Calculate individual stress scores
        face_stress_score = self._get_emotion_stress_score(face_emotion, face_confidence)
        speech_stress_score = self._get_emotion_stress_score(speech_emotion, speech_confidence)
        
        # Weighted combination
        combined_stress_score = (
            face_stress_score * self.face_weight + 
            speech_stress_score * self.speech_weight
        )
        
        # Update histories
        self.face_emotion_history.append((face_emotion, face_confidence))
        self.speech_emotion_history.append((speech_emotion, speech_confidence))
        
        # Apply temporal smoothing
        smoothed_score = self._apply_temporal_smoothing(combined_stress_score)
        
        # Determine stress level with multiple categories
        stress_level = self._get_stress_level(smoothed_score)
        
        # Update stress history with numeric values for better tracking
        self.stress_history.append(smoothed_score)
        
        # Create analysis details
        analysis_details = {
            'face_emotion': face_emotion,
            'face_confidence': face_confidence,
            'face_stress_score': face_stress_score,
            'speech_emotion': speech_emotion,
            'speech_confidence': speech_confidence,
            'speech_stress_score': speech_stress_score,
            'combined_score': combined_stress_score,
            'smoothed_score': smoothed_score,
            'stress_level': stress_level,
            'stress_numeric': self._get_stress_numeric(stress_level)
        }
        
        return stress_level, smoothed_score, analysis_details
    
    def _get_stress_level(self, stress_score):
        """
        Convert stress score to descriptive stress level
        
        Args:
            stress_score: normalized stress score (0-1)
            
        Returns:
            str: stress level description
        """
        if stress_score < 0.25:
            return "RELAXED"
        elif stress_score < 0.45:
            return "CALM"
        elif stress_score < 0.65:
            return "MILD STRESS"
        elif stress_score < 0.8:
            return "MODERATE STRESS"
        else:
            return "HIGH STRESS"
    
    def _get_stress_numeric(self, stress_level):
        """Get numeric value for stress level"""
        stress_map = {
            "RELAXED": 0,
            "CALM": 1,
            "MILD STRESS": 2,
            "MODERATE STRESS": 3,
            "HIGH STRESS": 4
        }
        return stress_map.get(stress_level, 1)
    
    def _get_stress_color(self, stress_level):
        """
        Get color tuple (BGR) for stress level visualization
        
        Args:
            stress_level: stress level string
            
        Returns:
            tuple: BGR color values
        """
        color_map = {
            "RELAXED": (0, 255, 0),      # Bright Green
            "CALM": (0, 200, 100),       # Light Green
            "MILD STRESS": (0, 255, 255), # Yellow
            "MODERATE STRESS": (0, 165, 255), # Orange
            "HIGH STRESS": (0, 0, 255)    # Red
        }
        return color_map.get(stress_level, (128, 128, 128))  # Default gray
    
    def _get_emotion_stress_score(self, emotion, confidence):
        """
        Convert emotion to stress score with more nuanced scoring
        
        Args:
            emotion: emotion label
            confidence: confidence score
            
        Returns:
            float: stress score (0-1)
        """
        if not emotion or confidence < 0.2:  # Very low confidence threshold
            return 0.3  # Default neutral stress
        
        # Enhanced emotion-to-stress mapping
        emotion_stress_map = {
            # High stress emotions
            'angry': 0.9,
            'fear': 0.85,
            'sad': 0.75,
            'disgust': 0.7,
            
            # Medium stress emotions
            'surprise': 0.5,  # Can be positive or negative
            
            # Low stress emotions
            'neutral': 0.3,
            'happy': 0.1,
        }
        
        base_score = emotion_stress_map.get(emotion, 0.4)
        
        # Apply confidence weighting
        confidence_weighted_score = base_score * confidence + 0.3 * (1 - confidence)
        
        return min(max(confidence_weighted_score, 0.0), 1.0)
    
    def _apply_temporal_smoothing(self, current_score):
        """
        Apply enhanced temporal smoothing with adaptive response
        
        Args:
            current_score: current stress score
            
        Returns:
            float: smoothed stress score
        """
        if len(self.stress_history) < 2:
            return current_score
        
        # Get recent history (last 5 samples)
        recent_history = list(self.stress_history)[-5:] if len(self.stress_history) >= 5 else list(self.stress_history)
        
        if not recent_history:
            return current_score
        
        # Calculate trend
        recent_avg = sum(recent_history) / len(recent_history)
        
        # Adaptive smoothing - more responsive to stress increases
        if current_score > recent_avg:
            # Stress increasing - respond faster
            alpha = 0.7  # Higher weight for current reading
        else:
            # Stress decreasing - smooth more
            alpha = 0.4  # Lower weight for current reading
        
        # Exponential smoothing
        smoothed = alpha * current_score + (1 - alpha) * recent_avg
        
        return smoothed
    
    def get_stress_statistics(self):
        """
        Get comprehensive stress statistics over recent history
        
        Returns:
            dict: detailed stress statistics
        """
        if not self.stress_history:
            return {
                'average_stress': 0,
                'current_level': 'CALM',
                'total_samples': 0,
                'stress_distribution': {},
                'trend': 'stable'
            }
        
        # Convert recent numeric scores to levels for distribution
        recent_scores = list(self.stress_history)[-20:]  # Last 20 readings
        recent_levels = [self._get_stress_level(score) for score in recent_scores]
        
        # Calculate distribution
        from collections import Counter
        level_counts = Counter(recent_levels)
        
        # Calculate trend
        if len(recent_scores) >= 5:
            first_half = sum(recent_scores[:len(recent_scores)//2]) / (len(recent_scores)//2)
            second_half = sum(recent_scores[len(recent_scores)//2:]) / (len(recent_scores) - len(recent_scores)//2)
            
            if second_half > first_half + 0.1:
                trend = 'increasing'
            elif second_half < first_half - 0.1:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'average_stress': sum(recent_scores) / len(recent_scores),
            'current_level': self._get_stress_level(recent_scores[-1]),
            'total_samples': len(self.stress_history),
            'stress_distribution': dict(level_counts),
            'trend': trend,
            'max_stress': max(recent_scores),
            'min_stress': min(recent_scores)
        }
    
    def reset_history(self):
        """Reset all emotion and stress histories"""
        self.face_emotion_history.clear()
        self.speech_emotion_history.clear()
        self.stress_history.clear()