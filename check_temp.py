from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz

# Connect to MongoDB
client = MongoClient('mongodb://10.0.1.252:27017/')
db = client["sensordata"]

# Get a sample document
sample = db.temperature_logs.find_one()
print("\nSample document from temperature_logs:")
print(sample)

# Get count of documents
count = db.temperature_logs.count_documents({})
print(f"\nTotal documents: {count}")

# Get the last 5 documents
print("\nLast 5 documents:")
for doc in db.temperature_logs.find().sort("timestamp", -1).limit(5):
    print(doc)

# Get unique room names
rooms = db.temperature_logs.distinct("room")
print("\nUnique room names:", rooms) 