"""
System Check Script
Verifies all components are properly installed and configured
"""

import sys
import os

def print_status(component, status, details=""):
    """Print component status with color coding"""
    if status:
        symbol = "✓"
        status_text = "OK"
    else:
        symbol = "✗"
        status_text = "FAILED"
    
    print(f"{symbol} {component:.<30} {status_text}")
    if details:
        print(f"  {details}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    is_ok = version.major == 3 and version.minor >= 11
    details = f"Python {version.major}.{version.minor}.{version.micro}"
    return is_ok, details

def check_module(module_name, display_name=None):
    """Check if a module can be imported"""
    if display_name is None:
        display_name = module_name
    
    try:
        __import__(module_name)
        return True, f"{display_name} installed"
    except ImportError as e:
        return False, f"{display_name} not found: {str(e)}"

def check_camera():
    """Check if camera is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        is_ok = cap.isOpened()
        cap.release()
        details = "Camera accessible" if is_ok else "Camera not found or in use"
        return is_ok, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_audio():
    """Check if audio devices are available"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        is_ok = len(input_devices) > 0
        details = f"Found {len(input_devices)} input device(s)" if is_ok else "No input devices found"
        return is_ok, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_database():
    """Check if database module works"""
    try:
        from database import StressDatabase
        db = StressDatabase(db_path=':memory:')  # Use in-memory DB for testing
        return True, "Database module OK"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_files():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'emotion_detector.py',
        'speech_detector.py',
        'stress_analyzer.py',
        'database.py',
        'requirements.txt',
        'templates/dashboard.html',
        'static/css/style.css',
        'static/js/dashboard.js'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    is_ok = len(missing) == 0
    details = "All files present" if is_ok else f"Missing: {', '.join(missing)}"
    return is_ok, details

def main():
    """Run all checks"""
    print("="*60)
    print("Worker Stress Analysis - System Check")
    print("="*60)
    print()
    
    all_ok = True
    
    # Check Python version
    status, details = check_python_version()
    print_status("Python Version", status, details)
    all_ok = all_ok and status
    
    # Check required files
    status, details = check_files()
    print_status("Required Files", status, details)
    all_ok = all_ok and status
    
    print()
    print("Checking Python Packages:")
    print("-" * 60)
    
    # Check core packages
    packages = [
        ('flask', 'Flask'),
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('torch', 'PyTorch'),
        ('fer', 'FER (Face Emotion Recognition)'),
        ('speechbrain', 'SpeechBrain'),
        ('sounddevice', 'SoundDevice'),
        ('librosa', 'Librosa')
    ]
    
    for module, display in packages:
        status, details = check_module(module, display)
        print_status(display, status, details if not status else "")
        all_ok = all_ok and status
    
    print()
    print("Checking Hardware:")
    print("-" * 60)
    
    # Check camera
    status, details = check_camera()
    print_status("Webcam", status, details)
    if not status:
        print("  Note: Camera may be in use by another application")
    
    # Check audio
    status, details = check_audio()
    print_status("Microphone", status, details)
    
    print()
    print("Checking Application Modules:")
    print("-" * 60)
    
    # Check custom modules
    custom_modules = [
        ('emotion_detector', 'Face Emotion Detector'),
        ('speech_detector', 'Speech Emotion Detector'),
        ('stress_analyzer', 'Stress Analyzer'),
        ('database', 'Database Handler')
    ]
    
    for module, display in custom_modules:
        status, details = check_module(module, display)
        print_status(display, status, details if not status else "")
        all_ok = all_ok and status
    
    # Check database functionality
    status, details = check_database()
    print_status("Database Functionality", status, details if not status else "")
    all_ok = all_ok and status
    
    print()
    print("="*60)
    if all_ok:
        print("✓ All checks passed! System is ready.")
        print()
        print("To start the application:")
        print("  python app.py")
        print()
        print("Then open your browser to: http://127.0.0.1:5000")
    else:
        print("✗ Some checks failed. Please resolve the issues above.")
        print()
        print("Common solutions:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Activate virtual environment: .\\venv311\\Scripts\\Activate.ps1")
        print("  3. Check camera/microphone connections")
        print("  4. Close other apps using camera/microphone")
    print("="*60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
