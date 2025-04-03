from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define timezone
EST = pytz.timezone('America/New_York')

# Function to convert UTC to EST
def convert_to_est(utc_dt):
    try:
        if isinstance(utc_dt, str):
            try:
                utc_dt = datetime.fromisoformat(utc_dt.replace("Z", "+00:00"))
            except Exception as e:
                logger.error(f"❌ Error parsing timestamp string: {utc_dt}")
                logger.error(f"   └─ Error details: {str(e)}")
                raise
        
        if not utc_dt.tzinfo:
            utc_dt = pytz.utc.localize(utc_dt)
        est_dt = utc_dt.astimezone(EST)
        return est_dt
    except Exception as e:
        logger.error(f"❌ Error converting to EST: {str(e)}")
        logger.error(f"   └─ Input datetime: {utc_dt}")
        raise

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB connection - use environment variable for connection string
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://10.0.1.252:27017/')
try:
    client = MongoClient(MONGO_URI)
    # Test the connection
    client.server_info()
    logger.info("Successfully connected to MongoDB")
    db = client["sensordata"]
    weather_collection = db["weatherData"]
    weather_collection = db["weatherData"]
    sensibo_collection = db["sensibo_logs"]
    temp_logs_collection = db["temperature_logs"]
    logger.info("Connected to all collections successfully")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    client = None

# Add a separator function for cleaner logs
def log_separator(message=""):
    logger.info("=" * 50)
    if message:
        logger.info(message)
        logger.info("=" * 50)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/combined-data")
def combined_data():
    try:
        log_separator("🔄 Starting Data Fetch")
        if not client:
            logger.error("❌ No MongoDB connection available")
            return jsonify({"error": "Database connection not available"}), 500

        # Get the last 24 hours of data in EST
        twenty_four_hours_ago = datetime.now(EST) - timedelta(hours=24)
        logger.info(f"Fetching data since: {twenty_four_hours_ago.isoformat()}")

        # Get weather data - convert the EST time back to UTC for query
        weather_query = {
            "Time Stamp": {
                "$gte": twenty_four_hours_ago.astimezone(pytz.UTC).isoformat()
            }
        }
        weather_data = list(weather_collection.find(weather_query).sort("Time Stamp", 1))
        weather_status = "✅" if len(weather_data) > 0 else "⚠️"
        logger.info(f"{weather_status} Weather Data: {len(weather_data)} points")
        if len(weather_data) > 0:
            logger.info(f"   └─ First weather timestamp: {weather_data[0].get('Time Stamp')}")
            logger.info(f"   └─ Last weather timestamp: {weather_data[-1].get('Time Stamp')}")

        # Get AC data - convert the EST time back to UTC for query
        ac_query = {
            "Timestamp": {
                "$gte": twenty_four_hours_ago.astimezone(pytz.UTC).isoformat()
            }
        }
        ac_data = list(sensibo_collection.find(ac_query).sort("Timestamp", 1))
        ac_status = "✅" if len(ac_data) > 0 else "⚠️"
        logger.info(f"{ac_status} AC Data: {len(ac_data)} points")
        if len(ac_data) > 0:
            logger.info(f"   └─ First AC timestamp: {ac_data[0].get('Timestamp')}")
            logger.info(f"   └─ Last AC timestamp: {ac_data[-1].get('Timestamp')}")

        # Get room temperature data - convert the EST time back to UTC for query
        room_query = {
            "Timestamp": {
                "$gte": twenty_four_hours_ago.astimezone(pytz.UTC).isoformat()
            }
        }
        room_data = list(temp_logs_collection.find(room_query).sort("Timestamp", 1))
        room_status = "✅" if len(room_data) > 0 else "⚠️"
        logger.info(f"{room_status} Room Data: {len(room_data)} points")
        if len(room_data) > 0:
            logger.info(f"   └─ First room timestamp: {room_data[0].get('Timestamp')}")
            logger.info(f"   └─ Last room timestamp: {room_data[-1].get('Timestamp')}")
            logger.info(f"   └─ Sample room data: {room_data[0]}")

        # Process and combine the data
        processed_data = {
            "timestamps": [],
            "outside_temp": [],
            "outside_feels_like": [],
            "outside_humidity": [],
            "ac_temp": [],
            "ac_humidity": [],
            "ac_feels_like": [],
            "room_temps": {},
            "room_humidity": {}
        }

        # Create a set of all unique timestamps
        all_timestamps = set()

        # Process weather data
        logger.info("📊 Processing weather data...")
        weather_points = {}
        for doc in weather_data:
            try:
                time_str = doc.get("Time Stamp")
                if isinstance(time_str, str):
                    # Parse the timestamp and convert to EST
                    time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    est_time = convert_to_est(time)
                    time_key = est_time.strftime("%Y-%m-%d %H:%M")
                    all_timestamps.add(time_key)
                    weather_points[time_key] = {
                        "temp": doc.get("Current Temperature"),
                        "feels_like": doc.get("Feels Like"),
                        "humidity": doc.get("Humidity")
                    }
                    logger.debug(f"   └─ Processed weather point: {time_key}")
            except Exception as e:
                logger.error(f"Error processing weather point: {str(e)}")
                continue

        # Process AC data
        logger.info("📊 Processing AC data...")
        ac_points = {}
        for doc in ac_data:
            try:
                timestamp = doc.get("Timestamp")
                if timestamp:
                    # Parse the timestamp and convert to EST
                    time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    est_time = convert_to_est(time)
                    time_key = est_time.strftime("%Y-%m-%d %H:%M")
                    all_timestamps.add(time_key)
                    ac_points[time_key] = {
                        "temp": doc.get("Temperature"),
                        "humidity": doc.get("Humidity"),
                        "feels_like": doc.get("Feels Like")
                    }
                    logger.debug(f"   └─ Processed AC point: {time_key}")
            except Exception as e:
                logger.error(f"Error processing AC point: {str(e)}")
                continue

        # Process room temperature data
        logger.info("📊 Processing room temperature data...")
        room_points = {}
        for doc in room_data:
            try:
                timestamp = doc.get("Timestamp")
                if timestamp:
                    # Parse the timestamp and convert to EST
                    time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    est_time = convert_to_est(time)
                    time_key = est_time.strftime("%Y-%m-%d %H:%M")
                    all_timestamps.add(time_key)
                    
                    room_name = doc.get("Room")
                    if room_name:
                        if room_name not in room_points:
                            room_points[room_name] = {}
                        room_points[room_name][time_key] = {
                            "temp": float(doc.get("Temperature")),
                            "humidity": float(doc.get("Humidity"))
                        }
                        logger.debug(f"   └─ Processed room point: {room_name} at {time_key}")
            except Exception as e:
                logger.error(f"Error processing room point: {str(e)}")
                continue

        # Sort timestamps
        sorted_timestamps = sorted(list(all_timestamps))
        processed_data["timestamps"] = sorted_timestamps

        # Initialize room data arrays
        for room_name in room_points:
            processed_data["room_temps"][room_name] = []
            processed_data["room_humidity"][room_name] = []

        # Fill in data points
        for ts in sorted_timestamps:
            # Weather data
            if ts in weather_points:
                processed_data["outside_temp"].append(weather_points[ts]["temp"])
                processed_data["outside_feels_like"].append(weather_points[ts]["feels_like"])
                processed_data["outside_humidity"].append(weather_points[ts]["humidity"])
            else:
                processed_data["outside_temp"].append(None)
                processed_data["outside_feels_like"].append(None)
                processed_data["outside_humidity"].append(None)

            # AC data
            if ts in ac_points:
                processed_data["ac_temp"].append(ac_points[ts]["temp"])
                processed_data["ac_humidity"].append(ac_points[ts]["humidity"])
                processed_data["ac_feels_like"].append(ac_points[ts]["feels_like"])
            else:
                processed_data["ac_temp"].append(None)
                processed_data["ac_humidity"].append(None)
                processed_data["ac_feels_like"].append(None)

            # Room data
            for room_name in room_points:
                if ts in room_points[room_name]:
                    processed_data["room_temps"][room_name].append(room_points[room_name][ts]["temp"])
                    processed_data["room_humidity"][room_name].append(room_points[room_name][ts]["humidity"])
                else:
                    processed_data["room_temps"][room_name].append(None)
                    processed_data["room_humidity"][room_name].append(None)

        # Log data summary
        log_separator("📈 Data Summary")
        logger.info(f"⏰ Total timestamps: {len(processed_data['timestamps'])}")
        logger.info(f"📅 Time range: {processed_data['timestamps'][0]} to {processed_data['timestamps'][-1]}")
        
        if len(processed_data['outside_temp']) > 0:
            outside_temps = list(filter(None, processed_data['outside_temp']))
            if outside_temps:
                logger.info(f"🌡️ Outside temp range: {min(outside_temps)}°F to {max(outside_temps)}°F")
        
        if len(processed_data['ac_temp']) > 0:
            ac_temps = list(filter(None, processed_data['ac_temp']))
            if ac_temps:
                logger.info(f"❄️ AC temp range: {min(ac_temps)}°F to {max(ac_temps)}°F")

        # Log room data summary
        for room_name in processed_data["room_temps"]:
            room_temps = list(filter(None, processed_data["room_temps"][room_name]))
            if room_temps:
                logger.info(f"🏠 {room_name} temp range: {min(room_temps)}°F to {max(room_temps)}°F")
        
        log_separator("✨ Request Complete")
        return jsonify(processed_data)
    except Exception as e:
        logger.error(f"❌ Error in combined_data route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/current-conditions")
def current_conditions():
    try:
        if not client:
            return jsonify({"error": "Database connection not available"}), 500

        # Get latest weather data
        latest_weather = weather_collection.find_one(sort=[("Time Stamp", -1)])
        
        # Get latest AC data
        latest_ac = sensibo_collection.find_one(sort=[("Timestamp", -1)])

        # Get latest room data for each room
        room_data = {}
        pipeline = [
            {
                "$sort": {"Timestamp": -1}
            },
            {
                "$group": {
                    "_id": "$Room",
                    "latest": {"$first": "$$ROOT"}
                }
            }
        ]
        latest_rooms = list(temp_logs_collection.aggregate(pipeline))
        
        for room in latest_rooms:
            room_name = room["_id"]
            latest = room["latest"]
            room_data[room_name] = {
                "temperature": float(latest.get("Temperature")),
                "humidity": float(latest.get("Humidity")),
                "timestamp": latest.get("Timestamp")
            }

        # Prepare response
        response = {
            "outside": {
                "temperature": latest_weather.get("Current Temperature") if latest_weather else None,
                "feels_like": latest_weather.get("Feels Like") if latest_weather else None,
                "humidity": latest_weather.get("Humidity") if latest_weather else None,
                "description": latest_weather.get("Description") if latest_weather else None,
                "icon": latest_weather.get("Icon") if latest_weather else None,
                "timestamp": latest_weather.get("Time Stamp") if latest_weather else None
            },
            "ac": {
                "temperature": latest_ac.get("Temperature") if latest_ac else None,
                "feels_like": latest_ac.get("Feels Like") if latest_ac else None,
                "humidity": latest_ac.get("Humidity") if latest_ac else None,
                "timestamp": latest_ac.get("Timestamp") if latest_ac else None
            },
            "rooms": room_data
        }

        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in current_conditions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/weather-data")
def weather_data():
    try:
        if not client:
            logger.error("No MongoDB connection available")
            return jsonify({"error": "Database connection not available"}), 500

        # Get the last 7 days of data in EST
        seven_days_ago = datetime.now(EST) - timedelta(days=7)
        
        # Query MongoDB for the data, sorting by timestamp
        cursor = weather_collection.find({
            "Time Stamp": {"$gte": seven_days_ago.isoformat()}
        }).sort("Time Stamp", 1)
        
        # Process the data
        data = []
        for doc in cursor:
            time_str = doc.get("Time Stamp")
            if isinstance(time_str, str):
                time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            else:
                time = time_str
            
            # Convert to EST
            est_time = convert_to_est(time)
            
            data.append({
                "time": est_time.strftime("%Y-%m-%d %H:%M"),
                "temperature": doc.get("Current Temperature"),
                "feels_like": doc.get("Feels Like"),
                "humidity": doc.get("Humidity"),
                "wind_speed": doc.get("Wind Speed"),
                "description": doc.get("Description"),
                "icon": doc.get("Icon")
            })
        
        logger.info(f"Retrieved {len(data)} weather records")
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/current-weather")
def current_weather():
    try:
        if not client:
            logger.error("No MongoDB connection available")
            return jsonify({"error": "Database connection not available"}), 500

        # Get the most recent weather data
        latest = weather_collection.find_one(sort=[("Time Stamp", -1)])
        
        if latest:
            logger.info("Retrieved latest weather data")
            
            # Convert timestamp to EST
            time_str = latest.get("Time Stamp")
            if time_str:
                est_time = convert_to_est(time_str)
                timestamp = est_time.strftime("%Y-%m-%d %H:%M")
            else:
                timestamp = None
            
            return jsonify({
                "location": latest.get("Location"),
                "temperature": latest.get("Current Temperature"),
                "feels_like": latest.get("Feels Like"),
                "humidity": latest.get("Humidity"),
                "wind_speed": latest.get("Wind Speed"),
                "description": latest.get("Description"),
                "icon": latest.get("Icon"),
                "timestamp": timestamp
            })
        
        logger.warning("No weather data found in database")
        return jsonify({"error": "No weather data available"}), 404
    except Exception as e:
        logger.error(f"Error fetching current weather: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/debug/data-count")
def debug_data_count():
    try:
        if not client:
            return jsonify({"error": "Database connection not available"}), 500
        weather_count = weather_collection.count_documents({})
        return jsonify({
            "weatherData_count": weather_count,
            "database": "sensordata",
            "collection": "weatherData"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/room-data/<room_name>")
def room_data(room_name):
    try:
        logger.info(f"🔍 Fetching data for room: {room_name}")
        if not client:
            logger.error("❌ Database connection not available")
            return jsonify({"error": "Database connection not available"}), 500

        # Get the last 24 hours of data in EST
        twenty_four_hours_ago = datetime.now(EST) - timedelta(hours=24)
        logger.info(f"📅 Fetching data since: {twenty_four_hours_ago.isoformat()}")
        
        # Query MongoDB for room data
        room_data = list(temp_logs_collection.find({
            "Room": room_name,
            "Timestamp": {
                "$gte": twenty_four_hours_ago.astimezone(pytz.UTC).isoformat()
            }
        }).sort("Timestamp", 1))

        logger.info(f"📊 Found {len(room_data)} records for room {room_name}")
        
        if not room_data:
            logger.warning(f"⚠️ No data found for room: {room_name}")
            # Try querying without the Room field as a fallback
            room_data = list(temp_logs_collection.find({
                "Timestamp": {
                    "$gte": twenty_four_hours_ago.astimezone(pytz.UTC).isoformat()
                }
            }).sort("Timestamp", 1))
            logger.info(f"📊 Found {len(room_data)} records in fallback query")
            if not room_data:
                logger.error(f"❌ No data found even in fallback query")
                return jsonify({"error": f"No data found for room: {room_name}"}), 404

        # Process data into hourly points
        hourly_data = {}
        skipped_records = 0
        for doc in room_data:
            try:
                timestamp = doc.get("Timestamp")
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                
                # Convert to EST and round to nearest hour
                est_time = convert_to_est(timestamp)
                hour_key = est_time.replace(minute=0, second=0, microsecond=0)
                
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = {
                        "temps": [],
                        "humidity": []
                    }
                
                # Handle temperature as string or number
                temp = doc.get("Temperature")
                if isinstance(temp, str):
                    temp = float(temp)
                
                # Handle humidity as number
                humidity = doc.get("Humidity")
                if humidity is not None:
                    humidity = float(humidity)
                
                hourly_data[hour_key]["temps"].append(temp)
                hourly_data[hour_key]["humidity"].append(humidity)
            except (ValueError, TypeError) as e:
                skipped_records += 1
                logger.error(f"❌ Error processing document: {doc}")
                logger.error(f"   └─ Error details: {str(e)}")
                continue

        # Calculate hourly averages
        processed_data = {
            "timestamps": [],
            "temperature": [],
            "humidity": []
        }

        for hour in sorted(hourly_data.keys()):
            processed_data["timestamps"].append(hour.isoformat())
            if hourly_data[hour]["temps"]:
                processed_data["temperature"].append(
                    sum(hourly_data[hour]["temps"]) / len(hourly_data[hour]["temps"])
                )
            if hourly_data[hour]["humidity"]:
                processed_data["humidity"].append(
                    sum(hourly_data[hour]["humidity"]) / len(hourly_data[hour]["humidity"])
                )

        logger.info(f"✨ Processing complete:")
        logger.info(f"   └─ Input records: {len(room_data)}")
        logger.info(f"   └─ Skipped records: {skipped_records}")
        logger.info(f"   └─ Output hourly points: {len(processed_data['timestamps'])}")
        logger.info(f"   └─ Sample data point: {processed_data['timestamps'][0] if processed_data['timestamps'] else 'None'}")
        logger.info(f"   └─ Temperature range: {min(processed_data['temperature'])} to {max(processed_data['temperature'])}")
        logger.info(f"   └─ Humidity range: {min(processed_data['humidity'])} to {max(processed_data['humidity'])}")
        
        return jsonify(processed_data)
    except Exception as e:
        logger.error(f"❌ Error in room_data endpoint: {str(e)}")
        logger.exception("Detailed traceback:")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
