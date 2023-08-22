import os
from dotenv import load_dotenv
from agixtsdk import AGiXTSDK

load_dotenv()
base_uri = os.getenv("AGIXT_URI", "http://localhost:7437")
agixt_api_key = os.getenv("AGIXT_API_KEY", "")
ApiClient = AGiXTSDK(base_uri=base_uri, api_key=agixt_api_key)

DEV_MODE = os.getenv("DEV_MODE", False)
