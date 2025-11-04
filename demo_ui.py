# Quick Start Script - Preview Professional UI
# This script launches the app with basic face detection to showcase the UI

from flask import Flask, render_template, Response, jsonify, request
import cv2
from datetime import datetime
import random
import json

app = Flask(__name__)

# Simple demo data generator
class DemoSystem:
    def __init__(self):
        self.stress_score = 0.3
        self.face_emotion = 'neutral'
        self.speech_emotion = 'neutral'
        self.face_confidence = 0.85
        self.speech_confidence = 0.75
        self.stress_level = 'CALM'
        self.total_samples = 42
        
    def get_current_state(self):
        # Simulate changing emotions
        emotions = ['happy', 'neutral', 'sad', 'angry', 'fear']
        if random.random() < 0.1:  # 10% chance to change
            self.face_emotion = random.choice(emotions)
            self.speech_emotion = random.choice(emotions)
            self.face_confidence = random.uniform(0.7, 0.95)
            self.speech_confidence = random.uniform(0.65, 0.90)
            
        # Simulate stress variation
        self.stress_score += random.uniform(-0.05, 0.05)
        self.stress_score = max(0, min(1, self.stress_score))
        
        # Update stress level
        if self.stress_score < 0.2:
            self.stress_level = 'RELAXED'
        elif self.stress_score < 0.4:
            self.stress_level = 'CALM'
        elif self.stress_score < 0.6:
            self.stress_level = 'MILD'
        elif self.stress_score < 0.8:
            self.stress_level = 'MODERATE'
        else:
            self.stress_level = 'HIGH'
            
        self.total_samples += 1
        
        return {
            'stress_score': self.stress_score,
            'stress_level': self.stress_level,
            'face_emotion': self.face_emotion,
            'face_confidence': self.face_confidence,
            'speech_emotion': self.speech_emotion,
            'speech_confidence': self.speech_confidence
        }

demo_system = DemoSystem()

# Video feed generator
def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Add "DEMO MODE" text
            cv2.putText(frame, 'DEMO MODE - Professional UI Preview', (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/current_state')
def current_state():
    return jsonify(demo_system.get_current_state())

@app.route('/api/statistics')
def statistics():
    return jsonify({
        'average_stress': demo_system.stress_score * 0.85,
        'max_stress': demo_system.stress_score * 1.15,
        'trend': random.choice(['stable', 'increasing', 'decreasing']),
        'total_samples': demo_system.total_samples
    })

@app.route('/api/history/recent')
def history_recent():
    limit = int(request.args.get('limit', 20))
    history = []
    for i in range(limit):
        history.append({
            'timestamp': (datetime.now()).isoformat(),
            'stress_score': random.uniform(0.2, 0.8),
            'stress_level': random.choice(['RELAXED', 'CALM', 'MILD', 'MODERATE']),
            'face_emotion': random.choice(['happy', 'neutral', 'sad']),
            'speech_emotion': random.choice(['happy', 'neutral', 'sad'])
        })
    return jsonify(history)

@app.route('/api/history/summary')
def history_summary():
    return jsonify({
        'face_emotion_distribution': {
            'happy': 45,
            'neutral': 32,
            'sad': 15,
            'angry': 5,
            'fear': 3
        }
    })

if __name__ == '__main__':
    print('\n' + '='*60)
    print('🎨 MindFlow - Professional UI Preview')
    print('='*60)
    print('\n✨ DEMO MODE - Showcasing Professional UI/UX Design')
    print('\n📊 Dashboard: http://localhost:5000')
    print('\n💡 Features:')
    print('   • Modern glassmorphism design')
    print('   • Spotify/Notion inspired interface')
    print('   • Real-time stress monitoring')
    print('   • Beautiful animations & transitions')
    print('\n⚡ Press Ctrl+C to stop')
    print('='*60 + '\n')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
