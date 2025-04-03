// Utility Functions
const formatTemperature = (temp) => temp ? `${Math.round(temp)}°F` : '--°F';
const formatHumidity = (humidity) => humidity ? `${Math.round(humidity)}%` : '--%';
const formatTimestamp = (timestamp) => {
    if (!timestamp) return '--';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
};

// Update Indicators
const updateTrendIndicator = (element, currentValue, previousValue) => {
    if (!currentValue || !previousValue) {
        element.innerHTML = '';
        return;
    }
    
    const diff = currentValue - previousValue;
    if (Math.abs(diff) < 0.1) {
        element.innerHTML = '<span class="text-text-secondary">→</span>';
        return;
    }
    
    if (diff > 0) {
        element.innerHTML = '<span class="trend-up">↑</span>';
    } else {
        element.innerHTML = '<span class="trend-down">↓</span>';
    }
};

// Card Update Functions
const updateOutdoorCard = (data) => {
    if (!data || !data.outside) return;
    
    const outside = data.outside;
    document.getElementById('outdoor-temp').textContent = formatTemperature(outside.temperature);
    document.getElementById('outdoor-feels-like').textContent = formatTemperature(outside.feels_like);
    document.getElementById('outdoor-humidity').textContent = formatHumidity(outside.humidity);
    document.getElementById('outdoor-condition').textContent = outside.description || '--';
    document.getElementById('outdoor-update').textContent = `Last updated: ${formatTimestamp(outside.timestamp)}`;
};

const updateIndoorCard = (data) => {
    if (!data || !data.rooms) return;
    
    const rooms = Object.values(data.rooms);
    if (rooms.length === 0) return;
    
    // Calculate averages
    const temps = rooms.map(r => r.temperature).filter(t => t !== null);
    const humidities = rooms.map(r => r.humidity).filter(h => h !== null);
    
    const avgTemp = temps.reduce((a, b) => a + b, 0) / temps.length;
    const avgHumidity = humidities.reduce((a, b) => a + b, 0) / humidities.length;
    
    // Update display
    document.getElementById('indoor-avg-temp').textContent = formatTemperature(avgTemp);
    document.getElementById('indoor-avg-humidity').textContent = formatHumidity(avgHumidity);
    document.getElementById('rooms-count').textContent = rooms.length;
    
    // Update timestamp using the most recent room update
    const latestTimestamp = Math.max(...rooms.map(r => new Date(r.timestamp)));
    document.getElementById('indoor-update').textContent = `Last updated: ${formatTimestamp(latestTimestamp)}`;
};

const updateACCard = (data) => {
    if (!data || !data.ac) return;
    
    const ac = data.ac;
    document.getElementById('ac-set-temp').textContent = formatTemperature(ac.temperature);
    document.getElementById('ac-humidity').textContent = formatHumidity(ac.humidity);
    document.getElementById('ac-mode').textContent = ac.mode || '--';
    document.getElementById('ac-status').textContent = ac.status || '--';
    document.getElementById('ac-update').textContent = `Last updated: ${formatTimestamp(ac.timestamp)}`;
};

// Chart Configuration
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        intersect: false,
        mode: 'index'
    },
    plugins: {
        legend: {
            position: 'top',
            labels: {
                color: '#B3B3B3',
                font: {
                    family: 'Inter'
                }
            }
        },
        tooltip: {
            backgroundColor: '#1E1E1E',
            titleColor: '#FFFFFF',
            bodyColor: '#B3B3B3',
            borderColor: '#BB86FC',
            borderWidth: 1,
            padding: 12,
            displayColors: true,
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += context.dataset.yAxisID === 'temperature' 
                            ? `${context.parsed.y.toFixed(1)}°F`
                            : `${context.parsed.y.toFixed(1)}%`;
                    }
                    return label;
                }
            }
        }
    },
    scales: {
        x: {
            type: 'time',
            time: {
                unit: 'hour',
                displayFormats: {
                    hour: 'ha'
                },
                parser: 'iso'
            },
            adapters: {
                date: {
                    zone: 'America/New_York'
                }
            },
            grid: {
                color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
                color: '#B3B3B3',
                maxRotation: 0
            }
        },
        temperature: {
            type: 'linear',
            position: 'left',
            grid: {
                color: 'rgba(255, 75, 75, 0.1)'
            },
            ticks: {
                color: '#FF4B4B',
                callback: value => `${value}°F`
            }
        },
        humidity: {
            type: 'linear',
            position: 'right',
            grid: {
                color: 'rgba(75, 158, 255, 0.1)'
            },
            ticks: {
                color: '#4B9EFF',
                callback: value => `${value}%`
            }
        }
    }
};

// Room Graph Functions
const createRoomGraph = async (roomName, currentData) => {
    console.log(`📊 Creating graph for room: ${roomName}`);
    console.log(`Current data:`, currentData);
    
    const template = document.getElementById('room-graph-template');
    const clone = template.content.cloneNode(true);
    
    // Set up card elements
    const card = clone.querySelector('.dashboard-card');
    card.id = `room-${roomName.toLowerCase().replace(/\s+/g, '-')}`;
    
    const title = clone.querySelector('.card-title');
    title.textContent = roomName;
    
    const tempValue = clone.querySelector('.metric-group:first-child .main-value');
    const humidityValue = clone.querySelector('.metric-group:last-child .main-value');
    
    // Set current values
    tempValue.textContent = formatTemperature(currentData.temperature);
    humidityValue.textContent = formatHumidity(currentData.humidity);
    
    // Set up chart
    const canvas = clone.querySelector('canvas');
    
    // Add to container first
    document.getElementById('room-graphs').appendChild(clone);
    console.log(`📦 Graph card added to container for ${roomName}`);
    
    try {
        console.log(`🔍 Fetching historical data for ${roomName}...`);
        // Fetch historical data for the room
        const response = await fetch(`/api/room-data/${encodeURIComponent(roomName)}`);
        console.log(`📡 API Response status:`, response.status);
        const historicalData = await response.json();
        console.log(`📥 Historical data received:`, historicalData);
        
        if (historicalData && historicalData.timestamps && historicalData.temperature && historicalData.humidity) {
            console.log(`✨ Creating data points for ${roomName}...`);
            // Create data points with proper timestamps
            const data = historicalData.timestamps.map((timestamp, index) => ({
                x: new Date(timestamp),
                y: historicalData.temperature[index]
            }));
            
            const humidityData = historicalData.timestamps.map((timestamp, index) => ({
                x: new Date(timestamp),
                y: historicalData.humidity[index]
            }));
            
            console.log(`📈 Temperature data points:`, data);
            console.log(`💧 Humidity data points:`, humidityData);
            
            console.log(`🎨 Creating chart for ${roomName}...`);
            const chart = new Chart(canvas, {
                type: 'line',
                data: {
                    datasets: [
                        {
                            label: 'Temperature',
                            yAxisID: 'temperature',
                            data: data,
                            borderColor: '#FF4B4B',
                            backgroundColor: 'rgba(255, 75, 75, 0.1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Humidity',
                            yAxisID: 'humidity',
                            data: humidityData,
                            borderColor: '#4B9EFF',
                            backgroundColor: 'rgba(75, 158, 255, 0.1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: chartOptions
            });
            
            console.log(`✅ Chart created successfully for ${roomName}`);
            
            // Store chart instance for updates
            card.dataset.chartInstance = chart;
        } else {
            console.error(`❌ Invalid data structure for ${roomName}:`, historicalData);
            throw new Error('Invalid data structure received from API');
        }
    } catch (error) {
        console.error(`❌ Error creating graph for ${roomName}:`, error);
        console.error('Error stack:', error.stack);
        canvas.parentElement.innerHTML = `
            <div class="flex items-center justify-center h-full text-error">
                <span>Failed to load graph data</span>
            </div>
        `;
    }
};

// Main update function
const updateDashboard = async () => {
    try {
        // Destroy existing charts before clearing the container
        const roomGraphs = document.getElementById('room-graphs');
        roomGraphs.querySelectorAll('.dashboard-card').forEach(card => {
            const chart = card.dataset.chartInstance;
            if (chart) {
                chart.destroy();
            }
        });
        roomGraphs.innerHTML = '';
        
        const response = await fetch('/api/current-conditions');
        const data = await response.json();
        
        updateOutdoorCard(data);
        updateIndoorCard(data);
        updateACCard(data);
        
        // Create room graphs
        if (data.rooms) {
            for (const [roomName, roomData] of Object.entries(data.rooms)) {
                await createRoomGraph(roomName, roomData);
            }
        }
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    // Update every minute
    setInterval(updateDashboard, 60000);
}); 