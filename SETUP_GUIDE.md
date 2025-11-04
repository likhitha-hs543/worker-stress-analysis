# Quick Setup Guide

## First Time Setup

1. Open PowerShell in the project directory
2. Create virtual environment:
   ```powershell
   python -m venv venv311
   ```

3. Activate virtual environment:
   ```powershell
   .\venv311\Scripts\Activate.ps1
   ```
   
   If you get an execution policy error, run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
   
   This will take 5-10 minutes and download ~500MB of models.

## Running the Application

### Option 1: Using Startup Script (Easiest)
Double-click `start_server.bat` or `start_server.ps1`

### Option 2: Manual
```powershell
.\venv311\Scripts\Activate.ps1
python app.py
```

## Accessing the Dashboard

Open your browser and go to:
```
http://127.0.0.1:5000
```

## What to Expect

1. **First Launch**: Models will be downloaded (one-time, ~2-3 minutes)
2. **Camera Permission**: Browser will ask for webcam access - click Allow
3. **Microphone Permission**: Browser will ask for microphone access - click Allow
4. **Dashboard Loading**: You should see:
   - Live video feed with face detection
   - Current stress level indicator
   - Real-time emotion displays
   - Charts updating automatically

## Stopping the Server

Press `Ctrl+C` in the terminal/command prompt

## Troubleshooting

### Camera Not Showing
- Make sure webcam is connected
- Close other apps using the camera (Zoom, Teams, etc.)
- Refresh the browser page

### "Module not found" errors
- Make sure you activated the virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

### High CPU Usage
- This is normal for real-time video processing
- Close other heavy applications
- Consider reducing video quality in app.py

### Database Errors
- Delete `stress_history.db` file
- Restart the application

## Features to Try

1. **Watch the stress level change** as you make different facial expressions
2. **Speak in different tones** to see speech emotion detection
3. **Check the history table** to see past readings
4. **View the charts** to see stress trends over time

## Data Storage

All data is stored in `stress_history.db` in the project folder.
To clear history: delete this file (it will be recreated automatically).

## Getting Help

Check the main README.md file for detailed documentation.
