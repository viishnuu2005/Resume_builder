"""
MongoDB Atlas connection and helper functions for users and resumes.
"""
import bcrypt
import certifi
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

# ── Connection ───────────────────────────────────────────────────────────────
MONGO_URI = "mongodb+srv://vishnuprasadp201_db_user:vishnu123@cluster0.tkdqh2c.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["resume_builder"]

users_col = db["users"]
resumes_col = db["resumes"]

# Ensure unique email index
users_col.create_index("email", unique=True)


# ── User Helpers ─────────────────────────────────────────────────────────────

def create_user(name: str, email: str, password: str) -> dict | None:
    """Register a new user. Returns the user dict or None if email exists."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        result = users_col.insert_one({
            "name": name,
            "email": email.lower().strip(),
            "password": hashed,
            "created_at": datetime.utcnow()
        })
        return {"_id": str(result.inserted_id), "name": name, "email": email}
    except Exception:
        return None  # duplicate email


def authenticate_user(email: str, password: str) -> dict | None:
    """Verify credentials. Returns user dict on success, None on failure."""
    user = users_col.find_one({"email": email.lower().strip()})
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return {"_id": str(user["_id"]), "name": user["name"], "email": user["email"]}
    return None


def get_user_by_id(user_id: str) -> dict | None:
    """Fetch user by ObjectId string."""
    try:
        user = users_col.find_one({"_id": ObjectId(user_id)})
        if user:
            return {"_id": str(user["_id"]), "name": user["name"], "email": user["email"]}
    except Exception:
        pass
    return None


# ── Resume Helpers ───────────────────────────────────────────────────────────

def save_resume(user_id: str, resume_data: dict) -> str:
    """Save a resume for a user. Returns the resume document ID."""
    doc = {
        "user_id": user_id,
        "data": resume_data,
        "created_at": datetime.utcnow()
    }
    result = resumes_col.insert_one(doc)
    return str(result.inserted_id)


def get_user_resumes(user_id: str) -> list:
    """Get all resumes for a user, newest first."""
    cursor = resumes_col.find({"user_id": user_id}).sort("created_at", -1)
    resumes = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        resumes.append(doc)
    return resumes


<<<<<<< HEAD
=======
def update_resume(resume_id: str, user_id: str, resume_data: dict) -> bool:
    """Update an existing resume document for the user."""
    try:
        result = resumes_col.update_one(
            {"_id": ObjectId(resume_id), "user_id": user_id},
            {"$set": {"data": resume_data, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    except Exception:
        return False


>>>>>>> e68d8668670d25dd91fd1abb36f5fc1903572a6a
def delete_resume(resume_id: str, user_id: str) -> bool:
    """Delete a resume by ID (only if it belongs to the user)."""
    try:
        result = resumes_col.delete_one({"_id": ObjectId(resume_id), "user_id": user_id})
        return result.deleted_count > 0
    except Exception:
        return False
