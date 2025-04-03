# Weather Dashboard

A Flask-based weather dashboard that displays and monitors temperature data from multiple sources including outdoor weather, AC, and room sensors.

## Features

- Real-time weather data display
- Indoor temperature monitoring from multiple room sensors
- AC system temperature and humidity tracking
- Historical data visualization
- REST API endpoints for data access
- Timezone-aware data handling (EST)

## Prerequisites

- Python 3.8+
- MongoDB
- Internet connection for weather data updates

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YourBr0ther/Weather-Dashboard.git
cd Weather-Dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your MongoDB connection string:
```
MONGO_URI=mongodb://your_mongodb_connection_string
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

## API Endpoints

- `/api/combined-data` - Get 24-hour historical data for all sensors
- `/api/current-conditions` - Get current conditions from all sensors
- `/api/weather-data` - Get 7-day weather history
- `/api/current-weather` - Get current weather conditions
- `/api/debug/data-count` - Get database record counts (debug endpoint)

## Project Structure

```
Weather-Dashboard/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static assets
├── templates/         # HTML templates
│   └── index.html    # Main dashboard template
└── .env              # Environment variables (not in repo)
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 