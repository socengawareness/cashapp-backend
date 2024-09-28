# app/database.py

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the database URL from the environment
MONGO_DETAILS = os.getenv("DATABASE_URL")

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.myAppDB  # Replace 'myAppDB' with your actual database name

users_collection = database.get_collection("users")


# Function to get user by login number
async def get_user_by_login_number(login_number: str):
    user = await users_collection.find_one(
        {"login_number": login_number}, {"_id": 0, "assigned_date": 0}
    )
    print(user)
    return user


# Function to create a new user (if needed)
async def create_user(user_data: dict):
    result = await users_collection.insert_one(user_data)
    return str(result.inserted_id)


async def update_user_device_id(login_number: str, device_id: str):
    await users_collection.update_one(
        {"login_number": login_number}, {"$set": {"device_id": device_id}}
    )
