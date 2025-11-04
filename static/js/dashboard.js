// Dashboard JavaScript for Real-time Updates

let stressChart = null;
let emotionChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    initializeCharts();
    updateCurrentTime();
    startRealTimeUpdates();
    
    // Update time every second
    setInterval(updateCurrentTime, 1000);
});

// Update current time display
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        month: 'short',
        day: 'numeric'
    });
    document.getElementById('currentTime').textContent = timeString;
}

// Start real-time updates
function startRealTimeUpdates() {
    // Update current state every second
    updateCurrentState();
    setInterval(updateCurrentState, 1000);
    
    // Update statistics every 5 seconds
    updateStatistics();
    setInterval(updateStatistics, 5000);
    
    // Update history every 10 seconds
    updateHistory();
    setInterval(updateHistory, 10000);
    
    // Update charts every 30 seconds
    updateCharts();
    setInterval(updateCharts, 30000);
}

// Fetch and update current state
async function updateCurrentState() {
    try {
        const response = await fetch('/api/current_state');
        const data = await response.json();
        
        console.log('Current state:', data); // Debug log
        
        // Update hero stats
        updateHeroStats(data);
        
        // Update emotion displays
        updateEmotionDisplay('face', data.face_emotion, data.face_confidence);
        updateEmotionDisplay('speech', data.speech_emotion, data.speech_confidence);
        
        // Update stress level
        updateStressLevel(data.stress_level, data.stress_score);
        updateStressGauge(data.stress_score, data.stress_level);
        
        // Update confidence rings
        updateConfidenceRing('faceRing', data.face_confidence);
        updateConfidenceRing('speechRing', data.speech_confidence);
        
    } catch (error) {
        console.error('Error updating current state:', error);
    }
}

// Update hero statistics cards
function updateHeroStats(data) {
    // Stress level
    const heroStressLevel = document.getElementById('heroStressLevel');
    const heroStressScore = document.getElementById('heroStressScore');
    if (heroStressLevel) heroStressLevel.textContent = data.stress_level;
    if (heroStressScore) heroStressScore.textContent = data.stress_score.toFixed(2);
    
    // Face emotion
    const heroFaceEmotion = document.getElementById('heroFaceEmotion');
    const heroFaceConfidence = document.getElementById('heroFaceConfidence');
    if (heroFaceEmotion) heroFaceEmotion.textContent = data.face_emotion;
    if (heroFaceConfidence) heroFaceConfidence.textContent = Math.round(data.face_confidence * 100) + '%';
    
    // Speech emotion
    const heroSpeechEmotion = document.getElementById('heroSpeechEmotion');
    const heroSpeechConfidence = document.getElementById('heroSpeechConfidence');
    if (heroSpeechEmotion) heroSpeechEmotion.textContent = data.speech_emotion;
    if (heroSpeechConfidence) heroSpeechConfidence.textContent = Math.round(data.speech_confidence * 100) + '%';
}

// Update emotion display cards
function updateEmotionDisplay(type, emotion, confidence) {
    const emotionIcons = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'fear': '😨',
        'neutral': '😐',
        'surprise': '😮',
        'disgust': '🤢'
    };
    
    // Update emoji
    const emoji = document.getElementById(`${type}Emoji`);
    if (emoji) emoji.textContent = emotionIcons[emotion] || '😐';
    
    // Update emotion name
    const nameElement = document.getElementById(`${type}EmotionName`);
    if (nameElement) {
        nameElement.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    }
    
    // Update confidence bar
    const fillElement = document.getElementById(`${type}ConfidenceFill`);
    if (fillElement) {
        fillElement.style.width = (confidence * 100) + '%';
    }
    
    // Update confidence text
    const textElement = document.getElementById(`${type}ConfidenceText`);
    if (textElement) {
        textElement.textContent = Math.round(confidence * 100) + '%';
    }
    
    // Update emotion breakdown bars (simulated data)
    updateEmotionBreakdown(emotion, confidence);
}

// Update emotion breakdown bars
function updateEmotionBreakdown(dominantEmotion, dominantConfidence) {
    const emotions = ['happy', 'neutral', 'sad', 'angry', 'fear'];
    const distribution = {};
    
    // Simulate distribution based on dominant emotion
    emotions.forEach(emotion => {
        if (emotion === dominantEmotion) {
            distribution[emotion] = dominantConfidence;
        } else {
            distribution[emotion] = (1 - dominantConfidence) / (emotions.length - 1);
        }
    });
    
    // Update bars
    emotions.forEach(emotion => {
        const item = document.querySelector(`.emotion-bar-item[data-emotion="${emotion}"]`);
        if (item) {
            const fill = item.querySelector('.emotion-bar-fill');
            const percent = item.querySelector('.emotion-percent');
            if (fill) fill.style.width = (distribution[emotion] * 100) + '%';
            if (percent) percent.textContent = Math.round(distribution[emotion] * 100) + '%';
        }
    });
}

// Update confidence ring
function updateConfidenceRing(ringId, confidence) {
    const ring = document.getElementById(ringId);
    if (ring) {
        const circle = ring.querySelector('.circle');
        if (circle) {
            const percentage = confidence * 100;
            circle.setAttribute('stroke-dasharray', `${percentage}, 100`);
        }
    }
}

// Update stress level display
function updateStressLevel(level, score) {
    // Update old elements (hidden but kept for compatibility)
    const levelText = document.getElementById('stressLevelText');
    const scoreText = document.getElementById('stressScore');
    const barFill = document.getElementById('stressBarFill');
    
    if (levelText) levelText.textContent = level;
    if (scoreText) scoreText.textContent = score.toFixed(3);
    if (barFill) barFill.style.width = (score * 100) + '%';
}

// Update stress gauge
function updateStressGauge(score, level) {
    const gaugeValue = document.getElementById('gaugeValue');
    const gaugeLabel = document.getElementById('gaugeLabel');
    const gaugeFill = document.getElementById('gaugeFill');
    
    if (gaugeValue) gaugeValue.textContent = score.toFixed(2);
    if (gaugeLabel) gaugeLabel.textContent = level;
    
    // Update gauge arc (SVG path)
    if (gaugeFill) {
        const percentage = score;
        const angle = 180 * percentage; // 180 degrees = semicircle
        const startX = 40;
        const startY = 150;
        const radius = 60;
        
        // Calculate end point
        const endAngle = (angle - 180) * (Math.PI / 180);
        const endX = 100 + radius * Math.cos(endAngle);
        const endY = 100 + radius * Math.sin(endAngle);
        
        const largeArc = angle > 180 ? 1 : 0;
        const path = `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArc} 1 ${endX} ${endY}`;
        
        gaugeFill.setAttribute('d', path);
        
        // Update color based on stress level
        let strokeColor = '#10b981'; // relaxed - green
        if (score > 0.2) strokeColor = '#3b82f6'; // calm - blue
        if (score > 0.4) strokeColor = '#f59e0b'; // mild - yellow
        if (score > 0.6) strokeColor = '#f97316'; // moderate - orange
        if (score > 0.8) strokeColor = '#ef4444'; // high - red
        
        gaugeFill.setAttribute('stroke', strokeColor);
    }
}

// Fetch and update statistics
async function updateStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        // Update statistics in quick stats cards
        const avgStress = document.getElementById('avgStress');
        const trend = document.getElementById('trend');
        const maxStress = document.getElementById('maxStress');
        const heroTotalSamples = document.getElementById('heroTotalSamples');
        const heroMaxStress = document.getElementById('heroMaxStress');
        
        if (avgStress) avgStress.textContent = (data.average_stress || 0).toFixed(2);
        if (trend) {
            trend.textContent = (data.trend || 'stable').charAt(0).toUpperCase() + (data.trend || 'stable').slice(1);
        }
        if (maxStress) maxStress.textContent = (data.max_stress || 0).toFixed(2);
        if (heroTotalSamples) heroTotalSamples.textContent = data.total_samples || 0;
        if (heroMaxStress) heroMaxStress.textContent = (data.max_stress || 0).toFixed(2);
        
        // Update trend indicator
        const trendIndicator = document.getElementById('trendIndicator');
        if (trendIndicator) {
            const trendText = data.trend === 'increasing' ? 'Rising' : 
                             data.trend === 'decreasing' ? 'Falling' : 'Stable';
            trendIndicator.textContent = trendText;
        }
        
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

// Fetch and update history table
async function updateHistory() {
    try {
        const response = await fetch('/api/history/recent?limit=20');
        const data = await response.json();
        
        const tbody = document.getElementById('historyTableBody');
        tbody.innerHTML = '';
        
        data.forEach(reading => {
            const row = document.createElement('tr');
            
            // Format timestamp
            const timestamp = new Date(reading.timestamp);
            const timeStr = timestamp.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            
            // Get stress badge class
            const badgeClass = reading.stress_level.toLowerCase().replace(' ', '-');
            
            row.innerHTML = `
                <td>${timeStr}</td>
                <td><span class="stress-badge ${badgeClass}">${reading.stress_level}</span></td>
                <td>${reading.stress_score.toFixed(3)}</td>
                <td>${reading.face_emotion}</td>
                <td>${reading.speech_emotion}</td>
            `;
            
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error updating history:', error);
    }
}

// Initialize charts
function initializeCharts() {
    // Stress history chart
    const stressCtx = document.getElementById('stressChart').getContext('2d');
    stressChart = new Chart(stressCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Stress Level',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    title: {
                        display: true,
                        text: 'Stress Score'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
    
    // Emotion distribution chart (Face emotions)
    const emotionCtx = document.getElementById('emotionChart').getContext('2d');
    emotionChart = new Chart(emotionCtx, {
        type: 'doughnut',
        data: {
            labels: ['Waiting for data...'],
            datasets: [{
                data: [1],
                backgroundColor: ['#e9ecef']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right'
                },
                title: {
                    display: false
                }
            }
        }
    });
}

// Update charts with fresh data
async function updateCharts() {
    try {
        // Update stress history chart
        const historyResponse = await fetch('/api/history/recent?limit=50');
        const historyData = await historyResponse.json();
        
        const labels = historyData.map(r => {
            const time = new Date(r.timestamp);
            return time.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }).reverse();
        
        const stressScores = historyData.map(r => r.stress_score).reverse();
        
        stressChart.data.labels = labels;
        stressChart.data.datasets[0].data = stressScores;
        stressChart.update();
        
        // Update emotion distribution chart with face emotions
        const summaryResponse = await fetch('/api/history/summary?hours=1');
        const summaryData = await summaryResponse.json();
        
        if (summaryData.face_emotion_distribution && Object.keys(summaryData.face_emotion_distribution).length > 0) {
            // Filter out null/None emotions
            const emotions = {};
            for (const [emotion, count] of Object.entries(summaryData.face_emotion_distribution)) {
                if (emotion && emotion !== 'null' && emotion !== 'None' && emotion !== '') {
                    emotions[emotion] = count;
                }
            }
            
            const emotionLabels = Object.keys(emotions);
            const emotionCounts = Object.values(emotions);
            
            // Only update if there's valid data
            if (emotionLabels.length > 0 && emotionCounts.length > 0) {
                emotionChart.data.labels = emotionLabels.map(e => e.charAt(0).toUpperCase() + e.slice(1));
                emotionChart.data.datasets[0].data = emotionCounts;
                emotionChart.update();
                console.log('Emotion chart updated with:', emotions);
            } else {
                // Show "no data" state
                emotionChart.data.labels = ['No data yet - waiting for face detection'];
                emotionChart.data.datasets[0].data = [1];
                emotionChart.data.datasets[0].backgroundColor = ['#e9ecef'];
                emotionChart.update();
            }
        } else {
            // Show "no data" state
            emotionChart.data.labels = ['No data yet - waiting for face detection'];
            emotionChart.data.datasets[0].data = [1];
            emotionChart.data.datasets[0].backgroundColor = ['#e9ecef'];
            emotionChart.update();
        }
        
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

// Helper function to format numbers
function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
