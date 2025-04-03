# Weather Dashboard Planning

## Vision
Create a modern, clean, dark-themed weather dashboard optimized for kitchen display, showing both indoor and outdoor climate data with easy-to-read visualizations.

## User Interface Design

### Top Section - Key Metrics Cards
1. **Outdoor Climate Card**
   - Current temperature
   - Feels like temperature
   - Humidity percentage
   - Weather icon/condition
   - Last updated timestamp

2. **Indoor Average Card**
   - Average temperature across all rooms
   - Average humidity across all rooms
   - Trend indicator (rising/falling)
   - Number of rooms included in average
   - Last updated timestamp

3. **AC Control Card (Sensibo)**
   - Set temperature
   - Current mode
   - Humidity level
   - System status
   - Last updated timestamp

### Bottom Section - Room Graphs
- Individual graph cards for each room
- Hourly data points (no sub-hour markers)
- 24-hour timeline
- Dual Y-axis for temperature and humidity
- Room name and current values in header
- Minimalist design with clear data points

## Technical Specifications

### Data Management
- MongoDB collections structure:
  ```
  weatherData: {
    timestamp: DateTime,
    temperature: Float,
    feels_like: Float,
    humidity: Float,
    description: String,
    icon: String
  }

  room_sensors: {
    timestamp: DateTime,
    room_id: String,
    room_name: String,
    temperature: Float,
    humidity: Float
  }

  sensibo_data: {
    timestamp: DateTime,
    set_temperature: Float,
    current_temperature: Float,
    humidity: Float,
    mode: String,
    status: String
  }
  ```

### API Endpoints
- GET `/api/dashboard-data`
  - Returns all data needed for initial dashboard render
- GET `/api/room-data/{room_id}`
  - Returns 24h historical data for specific room
- GET `/api/average-conditions`
  - Returns current averaged indoor conditions

### UI/UX Design Elements
- Color Scheme:
  - Background: #121212 (Material Dark)
  - Card Background: #1E1E1E
  - Primary Text: #FFFFFF
  - Secondary Text: #B3B3B3
  - Accent: #BB86FC
  - Error: #CF6679
  - Graph Lines:
    - Temperature: #FF4B4B
    - Humidity: #4B9EFF

- Typography:
  - Primary Font: Inter
  - Monospace: JetBrains Mono (for numbers)
  - Font Sizes:
    - Card Titles: 1.25rem
    - Main Values: 2.5rem
    - Labels: 0.875rem

- Card Design:
  - Subtle border radius: 12px
  - Minimal shadow
  - Semi-transparent overlays
  - Smooth hover effects

### Auto-Refresh Strategy
- Main metrics: Every 60 seconds
- Graphs: Every 5 minutes
- Smooth transitions for data updates
- Clear loading states

### Responsive Design
- Breakpoints:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
- Flexible grid system
- Adaptive graph sizing
- Touch-friendly on mobile devices

## Performance Considerations
- Data aggregation at server level
- Client-side caching
- Optimized graph rendering
- Lazy loading for historical data
- Compressed API responses

## Future Enhancements
1. Room customization (names, icons)
2. Temperature alerts/notifications
3. Historical data analysis
4. Export functionality
5. Additional sensor integration
6. Weather forecasting
7. Energy usage correlation 