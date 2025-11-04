"""
Flask Web Application for Worker Stress Analysis
Real-time face and speech emotion detection with dashboard
"""

import cv2
import time
import json
from flask import Flask, render_template, Response, jsonify, request
from datetime import datetime
import threading
from emotion_detector import FaceEmotionDetector
from speech_detector import SpeechEmotionDetector
from stress_analyzer import StressAnalyzer
from database import StressDatabase

app = Flask(__name__)

# Global variables for the stress analysis system
face_detector = None
speech_detector = None
stress_analyzer = None
database = None
camera = None

# Current state variables
current_state = {
    'face_emotion': 'neutral',
    'face_confidence': 0.0,
    'speech_emotion': 'neutral',
    'speech_confidence': 0.0,
    'stress_level': 'CALM',
    'stress_score': 0.0,
    'timestamp': datetime.now().isoformat()
}

# Lock for thread-safe operations
state_lock = threading.Lock()

def initialize_system():
    """Initialize all components of the stress analysis system"""
    global face_detector, speech_detector, stress_analyzer, database, camera
    
    print("Initializing Worker Stress Analysis System...")
    
    # Initialize detectors
    face_detector = FaceEmotionDetector()
    speech_detector = SpeechEmotionDetector()
    stress_analyzer = StressAnalyzer()
    database = StressDatabase()
    
    # Initialize camera
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 15)
    
    # Start speech detection
    speech_detector.start_recording()
    
    # Start background processing thread
    processing_thread = threading.Thread(target=process_emotions, daemon=True)
    processing_thread.start()
    
    print("System initialized successfully!")

def process_emotions():
    """Background thread to continuously process emotions and update state"""
    global current_state
    
    last_save_time = time.time()
    last_log_time = time.time()
    save_interval = 5.0  # Save to database every 5 seconds
    log_interval = 10.0  # Log status every 10 seconds
    
    while True:
        try:
            # Get speech emotion
            speech_emotion, speech_conf = speech_detector.get_current_emotion()
            
            # Analyze stress
            stress_level, stress_score, details = stress_analyzer.analyze_stress(
                current_state['face_emotion'],
                current_state['face_confidence'],
                speech_emotion,
                speech_conf
            )
            
            # Update current state (thread-safe)
            with state_lock:
                current_state.update({
                    'speech_emotion': speech_emotion,
                    'speech_confidence': speech_conf,
                    'stress_level': stress_level,
                    'stress_score': stress_score,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Log status periodically
            current_time = time.time()
            if current_time - last_log_time >= log_interval:
                stats = speech_detector.get_statistics()
                print(f"\n📊 Status Update:")
                print(f"   Face: {current_state['face_emotion']} ({current_state['face_confidence']:.2f})")
                print(f"   Speech: {speech_emotion} ({speech_conf:.2f}) - {stats['speech_chunks']} speech chunks detected")
                print(f"   Stress: {stress_level} ({stress_score:.2f})")
                last_log_time = current_time
            
            # Save to database periodically
            if current_time - last_save_time >= save_interval:
                database.save_stress_reading(
                    current_state['face_emotion'],
                    current_state['face_confidence'],
                    current_state['speech_emotion'],
                    current_state['speech_confidence'],
                    current_state['stress_level'],
                    current_state['stress_score']
                )
                last_save_time = current_time
            
            time.sleep(0.5)  # Update every 500ms
            
        except Exception as e:
            print(f"Processing error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(1)

def generate_frames():
    """Generate video frames with emotion detection"""
    global current_state
    
    while True:
        try:
            success, frame = camera.read()
            if not success:
                break
            
            # Detect face emotion
            face_emotion, face_conf, face_coords = face_detector.detect_emotion(frame)
            
            if face_emotion:
                with state_lock:
                    current_state['face_emotion'] = face_emotion
                    current_state['face_confidence'] = face_conf
            
            # Draw results on frame (without text overlay, that's for dashboard)
            if face_coords:
                x, y, w, h = face_coords
                # Draw simple rectangle
                color = get_stress_color(current_state['stress_level'])
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
        except Exception as e:
            print(f"Frame generation error: {e}")
            continue

def get_stress_color(stress_level):
    """Get BGR color for stress level"""
    colors = {
        "RELAXED": (0, 255, 0),
        "CALM": (0, 200, 100),
        "MILD STRESS": (0, 255, 255),
        "MODERATE STRESS": (0, 165, 255),
        "HIGH STRESS": (0, 0, 255)
    }
    return colors.get(stress_level, (128, 128, 128))

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/current_state')
def get_current_state():
    """API endpoint to get current stress state"""
    with state_lock:
        state_copy = current_state.copy()
    return jsonify(state_copy)

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get stress statistics"""
    stats = stress_analyzer.get_stress_statistics()
    return jsonify(stats)

@app.route('/api/history')
def get_history():
    """API endpoint to get stress history from database"""
    hours = int(request.args.get('hours', 1))
    history = database.get_history(hours)
    return jsonify(history)

@app.route('/api/history/recent')
def get_recent_history():
    """API endpoint to get recent stress readings"""
    limit = int(request.args.get('limit', 50))
    history = database.get_recent_readings(limit)
    return jsonify(history)

@app.route('/api/history/summary')
def get_history_summary():
    """API endpoint to get summary statistics"""
    hours = int(request.args.get('hours', 24))
    summary = database.get_summary_stats(hours)
    return jsonify(summary)

if __name__ == '__main__':
    initialize_system()
    print("\n" + "="*60)
    print("  WORKER STRESS ANALYSIS - WEB DASHBOARD")
    print("="*60)
    print("  Access the dashboard at: http://127.0.0.1:5000")
    print("  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
        if speech_detector:
            speech_detector.stop_recording()
        if camera:
            camera.release()
