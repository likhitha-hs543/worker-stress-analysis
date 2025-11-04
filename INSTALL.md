# Installation Instructions

## Step-by-Step Installation Guide

### 1. Prerequisites Check
Before starting, ensure you have:
- [ ] Python 3.11 installed
- [ ] Webcam connected
- [ ] Microphone connected
- [ ] At least 2GB free disk space
- [ ] Internet connection (for downloading packages and models)

Check Python version:
```powershell
python --version
```
Should show Python 3.11.x

### 2. Create Virtual Environment
Open PowerShell in the project directory:
```powershell
cd "d:\worker-stress-analysis - Copy"
python -m venv venv311
```

### 3. Activate Virtual Environment

**PowerShell:**
```powershell
.\venv311\Scripts\Activate.ps1
```

**If you get an execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

**Command Prompt:**
```cmd
.\venv311\Scripts\activate.bat
```

You should see `(venv311)` at the start of your command prompt.

### 4. Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### 5. Install Dependencies
This will take 5-10 minutes:
```powershell
pip install -r requirements.txt
```

**Expected output:**
- Installing OpenCV, TensorFlow, PyTorch, etc.
- Total download size: ~500MB
- Installation might show warnings (usually safe to ignore)

### 6. Verify Installation
Test if key packages are installed:
```powershell
python -c "import flask; import cv2; import torch; print('All packages installed successfully!')"
```

### 7. First Run
Start the application:
```powershell
python app.py
```

**What to expect:**
- "Loading speech emotion model..." (may take 1-2 minutes first time)
- Models downloading to `pretrained_models/` folder
- "System initialized successfully!"
- "Access the dashboard at: http://127.0.0.1:5000"

### 8. Open Dashboard
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

Grant camera and microphone permissions when prompted.

## Common Installation Issues

### Issue: "python is not recognized"
**Solution:** Add Python to PATH or use full path to python.exe

### Issue: pip install fails with "ERROR: Could not build wheels"
**Solution:** 
```powershell
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

### Issue: TensorFlow or PyTorch installation fails
**Solution:** Install separately:
```powershell
pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
pip install tensorflow==2.20.0
pip install -r requirements.txt
```

### Issue: "Execution policy" error on PowerShell
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Out of memory during installation
**Solution:** Install packages one at a time:
```powershell
pip install flask flask-cors
pip install opencv-python
pip install fer
pip install torch torchaudio
pip install speechbrain
pip install sounddevice librosa
```

## Verifying Everything Works

After installation, verify each component:

### 1. Check Flask
```powershell
python -c "from flask import Flask; print('Flask OK')"
```

### 2. Check OpenCV (Camera)
```powershell
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAILED'); cap.release()"
```

### 3. Check Audio
```powershell
python -c "import sounddevice as sd; print('Audio OK')"
```

### 4. Check Face Detection
```powershell
python -c "from fer import FER; detector = FER(); print('Face detection OK')"
```

## Quick Start After Installation

1. Activate virtual environment:
   ```powershell
   .\venv311\Scripts\Activate.ps1
   ```

2. Run application:
   ```powershell
   python app.py
   ```
   OR double-click `start_server.bat`

3. Open browser to `http://127.0.0.1:5000`

## Uninstallation

To completely remove:
1. Delete the project folder
2. (Optional) Reset execution policy:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Default -Scope CurrentUser
   ```

## Getting Help

If you encounter issues:
1. Check this installation guide
2. Review SETUP_GUIDE.md
3. Check README.md troubleshooting section
4. Ensure all prerequisites are met
