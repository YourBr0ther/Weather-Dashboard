from pymongo import MongoClient
from datetime import datetime
import pytz

# Connect to MongoDB
client = MongoClient('mongodb://10.0.1.252:27017/')
db = client["sensordata"]

# Function to print document in a readable format
def print_doc(doc):
    for key, value in doc.items():
        print(f"{key}: {value}")
    print("-" * 50)

# Check sensibo_logs collection
print("\n=== Latest 3 entries from sensibo_logs ===")
for doc in db.sensibo_logs.find().sort("timestamp", -1).limit(3):
    print_doc(doc)

# Check weatherData collection
print("\n=== Latest 3 entries from weatherData ===")
for doc in db.weatherData.find().sort("Time Stamp", -1).limit(3):
    print_doc(doc)

# Check Temperature_logs collection
print("\n=== Latest 3 entries from Temperature_logs ===")
for doc in db.Temperature_logs.find().sort("timestamp", -1).limit(3):
    print_doc(doc)

# Print collection stats
print("\n=== Collection Stats ===")
print(f"sensibo_logs count: {db.sensibo_logs.count_documents({})}")
print(f"weatherData count: {db.weatherData.count_documents({})}")
print(f"Temperature_logs count: {db.Temperature_logs.count_documents({})}")

# Check time ranges
print("\n=== Time Ranges ===")
for collection_name in ["sensibo_logs", "weatherData", "Temperature_logs"]:
    collection = db[collection_name]
    time_field = "Time Stamp" if collection_name == "weatherData" else "timestamp"
    
    earliest = collection.find_one(sort=[(time_field, 1)])
    latest = collection.find_one(sort=[(time_field, -1)])
    
    if earliest and latest:
        print(f"\n{collection_name}:")
        print(f"Earliest: {earliest.get(time_field)}")
        print(f"Latest: {latest.get(time_field)}") 