from components.Auth import hide_pages, get_user
from Globals import getenv
from agixtsdk import AGiXTSDK


def get_agixt():
    hide_pages()
    user = get_user()
    if "token" in user:
        return AGiXTSDK(base_uri=getenv("AGIXT_URI"), api_key=user["token"])
    return None
