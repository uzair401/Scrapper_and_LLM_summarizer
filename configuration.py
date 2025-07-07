import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LinkedIn API Configuration
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URI = 'http://52.20.1.111'

# FastAPI Configuration
FASTAPI_URL = os.getenv('FASTAPI_URL', 'localhost')

def validate_config():
    """Validate that all required configuration is present"""
    missing = []
    if not LINKEDIN_CLIENT_ID:
        missing.append('LINKEDIN_CLIENT_ID')
    if not LINKEDIN_CLIENT_SECRET:
        missing.append('LINKEDIN_CLIENT_SECRET')
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        return True

