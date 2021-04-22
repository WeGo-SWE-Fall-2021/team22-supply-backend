# Small utils for mongo db
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_secret = os.getenv("MONGO_SECRET")

def checkUserInDatabase(self):
    return True


def initMongoFromCloud(cloud):
    return MongoClient('localhost:27017',
                       username="developer",
                       password=f"{mongo_secret}",
                       authSource=f"team22_{cloud}")
