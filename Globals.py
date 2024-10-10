import os
from dotenv import load_dotenv

load_dotenv()


def getenv(var_name: str):
    default_values = {
        "APP_NAME": "AGiXT",
        "AGIXT_URI": "http://agixt:7437",
        "AUTH_PROVIDER": "magicalauth",
        "APP_URI": "http://localhost:8501",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "%(asctime)s | %(levelname)s | %(message)s",
        "PRIMARY_COLOR": "#4CAF50",
        "BACKGROUND_COLOR": "#F0F0F0",
        "SECONDARY_BACKGROUND_COLOR": "#E0E0E0",
        "TEXT_COLOR": "#333333",
        "FONT": "sans-serif"
    }
    default_value = default_values[var_name] if var_name in default_values else ""
    return os.getenv(var_name, default_value)
