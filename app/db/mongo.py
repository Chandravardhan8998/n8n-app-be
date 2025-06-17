import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

load_dotenv()
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASS")
import certifi
ca = certifi.where()

uri = f"mongodb+srv://{username}:{password}@cluster0.bv1rtx0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = AsyncIOMotorClient(uri)

client = AsyncIOMotorClient(
    uri,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["db_name"]  # use your DB name

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

node_collection=db["nodes"]
flow_collection=db["flow"]