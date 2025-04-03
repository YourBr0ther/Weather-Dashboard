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

// Room Graph Functions
const createRoomGraph = (roomName, data) => {
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
    tempValue.textContent = formatTemperature(data.temperature);
    humidityValue.textContent = formatHumidity(data.humidity);
    
    // Set up chart
    const canvas = clone.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    
    // Chart configuration will be added in the next step
    
    // Add to container
    document.getElementById('room-graphs').appendChild(clone);
};

// Main update function
const updateDashboard = async () => {
    try {
        const response = await fetch('/api/current-conditions');
        const data = await response.json();
        
        updateOutdoorCard(data);
        updateIndoorCard(data);
        updateACCard(data);
        
        // Handle room graphs
        const roomGraphs = document.getElementById('room-graphs');
        roomGraphs.innerHTML = ''; // Clear existing graphs
        
        if (data.rooms) {
            Object.entries(data.rooms).forEach(([roomName, roomData]) => {
                createRoomGraph(roomName, roomData);
            });
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