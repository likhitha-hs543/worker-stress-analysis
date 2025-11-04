# System Architecture

## Overview
```
┌─────────────────────────────────────────────────────────────┐
│                     USER'S BROWSER                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Dashboard Interface                     │   │
│  │  • Live Video Feed                                  │   │
│  │  • Stress Level Display                             │   │
│  │  • Real-time Charts                                 │   │
│  │  • History Table                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    FLASK WEB SERVER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  app.py - Main Application                           │  │
│  │  • Route Handlers                                    │  │
│  │  • Video Streaming                                   │  │
│  │  • API Endpoints                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└───────┬────────────────┬────────────────┬───────────────────┘
        │                │                │
        ↓                ↓                ↓
┌───────────────┐ ┌──────────────┐ ┌─────────────────┐
│Face Emotion   │ │Speech Emotion│ │Stress Analyzer  │
│Detector       │ │Detector      │ │                 │
│(FER + MTCNN)  │ │(SpeechBrain) │ │Combines both    │
└───────┬───────┘ └──────┬───────┘ └────────┬────────┘
        │                │                   │
        └────────────────┴───────────────────┘
                         │
                         ↓
                ┌─────────────────┐
                │  SQLite DB      │
                │stress_history.db│
                └─────────────────┘
```

## Data Flow

### 1. Input Processing
```
Webcam → Face Detection → Emotion Classification → Confidence Score
                              (angry, happy, sad, etc.)

Microphone → Audio Processing → Speech Emotion → Confidence Score
                                  (angry, happy, sad, etc.)
```

### 2. Stress Analysis
```
Face Emotion + Speech Emotion → Weighted Combination → Stress Score
                                                        (0.0 - 1.0)
                                      ↓
                              Stress Level Classification
                                      ↓
                    RELAXED | CALM | MILD | MODERATE | HIGH
```

### 3. Data Storage
```
Every 5 seconds:
  Current State → Database
    • Timestamp
    • Face Emotion + Confidence
    • Speech Emotion + Confidence  
    • Stress Level
    • Stress Score
```

### 4. Dashboard Updates
```
Every 1 second:  Update current stress display
Every 5 seconds: Update statistics
Every 10 seconds: Update history table
Every 30 seconds: Update charts
```

## File Structure & Responsibilities

### Backend (Python)
- **app.py**: Main Flask application, handles HTTP requests, manages threads
- **emotion_detector.py**: Face emotion detection using FER library
- **speech_detector.py**: Speech emotion detection using SpeechBrain
- **stress_analyzer.py**: Combines emotions to calculate stress level
- **database.py**: SQLite database operations for history storage

### Frontend (HTML/CSS/JS)
- **dashboard.html**: Main dashboard layout and structure
- **style.css**: Styling, colors, responsive design
- **dashboard.js**: Real-time data fetching and UI updates

### Data Storage
- **stress_history.db**: SQLite database with readings table

## API Endpoints

| Endpoint | Method | Description | Update Frequency |
|----------|--------|-------------|------------------|
| `/` | GET | Dashboard page | - |
| `/video_feed` | GET | MJPEG video stream | Real-time |
| `/api/current_state` | GET | Current emotions & stress | 1s |
| `/api/statistics` | GET | Aggregate statistics | 5s |
| `/api/history/recent` | GET | Last N readings | 10s |
| `/api/history/summary` | GET | Summary stats | On demand |

## Threading Model

```
Main Thread:
  ├─ Flask HTTP Server
  └─ Video Frame Generation

Background Thread 1:
  └─ Emotion Processing & Analysis
      ├─ Get speech emotion
      ├─ Calculate stress
      └─ Save to database

Background Thread 2:
  └─ Audio Recording
      └─ Continuous microphone input
```

## Performance Considerations

- **Face Detection**: Every 3rd frame (reduces CPU load)
- **Speech Processing**: 500ms chunks with 500ms intervals
- **Database Writes**: Batched every 5 seconds
- **Video Streaming**: 15 FPS default
- **Dashboard Updates**: Staggered intervals to reduce load

## Security Notes

- All processing is local (no external API calls)
- Database is local SQLite file
- No data transmission to external servers
- Camera/mic access only within the application
