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
        
        // Update face emotion (old display)
        document.getElementById('faceEmotion').textContent = data.face_emotion;
        document.getElementById('faceConfidence').textContent = data.face_confidence.toFixed(2);
        
        // Update speech emotion (old display)
        document.getElementById('speechEmotion').textContent = data.speech_emotion;
        document.getElementById('speechConfidence').textContent = data.speech_confidence.toFixed(2);
        
        // Update emotion classification cards (new display)
        updateEmotionCard('face', data.face_emotion, data.face_confidence);
        updateEmotionCard('speech', data.speech_emotion, data.speech_confidence);
        
        // Update stress level
        updateStressLevel(data.stress_level, data.stress_score);
        
    } catch (error) {
        console.error('Error updating current state:', error);
    }
}

// Update emotion classification cards
function updateEmotionCard(type, emotion, confidence) {
    const nameElement = document.getElementById(`${type}EmotionName`);
    const barElement = document.getElementById(`${type}ConfidenceBar`);
    const textElement = document.getElementById(`${type}ConfidenceText`);
    
    if (nameElement && barElement && textElement) {
        // Update emotion name
        nameElement.textContent = emotion;
        nameElement.className = 'emotion-name ' + emotion;
        
        // Update confidence bar
        const percentage = Math.round(confidence * 100);
        barElement.style.width = percentage + '%';
        barElement.className = 'emotion-confidence-fill ' + emotion;
        
        // Update confidence text
        textElement.textContent = percentage + '%';
        
        // Update icon based on emotion
        const card = document.querySelector(`.${type}-emotion-card`);
        const icon = card.querySelector('.emotion-icon');
        if (icon) {
            const emotionIcons = {
                'happy': '😊',
                'sad': '😢',
                'angry': '😠',
                'fear': '😨',
                'neutral': '😐',
                'surprise': '😮',
                'disgust': '🤢'
            };
            icon.textContent = emotionIcons[emotion] || '😐';
        }
    }
}

// Update stress level display
function updateStressLevel(level, score) {
    const indicator = document.getElementById('stressIndicator');
    const levelText = document.getElementById('stressLevelText');
    const scoreText = document.getElementById('stressScore');
    const barFill = document.getElementById('stressBarFill');
    
    // Update text
    levelText.textContent = level;
    scoreText.textContent = score.toFixed(3);
    
    // Update stress bar
    barFill.style.width = (score * 100) + '%';
    
    // Remove all stress classes
    indicator.className = 'stress-indicator';
    
    // Add appropriate class based on level
    const levelClass = level.toLowerCase().replace(' ', '-');
    indicator.classList.add('stress-' + levelClass);
}

// Fetch and update statistics
async function updateStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        // Update statistics
        document.getElementById('avgStress').textContent = 
            (data.average_stress || 0).toFixed(3);
        document.getElementById('trend').textContent = data.trend || 'stable';
        document.getElementById('totalSamples').textContent = data.total_samples || 0;
        document.getElementById('maxStress').textContent = 
            (data.max_stress || 0).toFixed(3);
        
        // Update trend color
        const trendElement = document.getElementById('trend');
        trendElement.className = 'stat-value';
        if (data.trend === 'increasing') {
            trendElement.style.color = '#dc3545';
        } else if (data.trend === 'decreasing') {
            trendElement.style.color = '#28a745';
        } else {
            trendElement.style.color = '#fff';
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
