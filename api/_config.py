import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-prod")
JWT_ACCESS_TTL = int(os.getenv("JWT_ACCESS_TTL", "3600"))    # 1 hour
JWT_REFRESH_TTL = int(os.getenv("JWT_REFRESH_TTL", "604800")) # 7 days
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
