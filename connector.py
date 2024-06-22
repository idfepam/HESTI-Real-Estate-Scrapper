import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["real_estate"]
collection = db["land_listings"]
