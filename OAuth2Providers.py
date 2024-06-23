from Globals import getenv


def get_provider_info(provider):
    providers = {
        "amazon": {
            "scopes": ["openid", "email", "profile"],
            "authorization_url": f"https://{getenv('AWS_USER_POOL_ID')}.auth.{getenv('AWS_REGION')}.amazoncognito.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        },
        "aol": {
            "scopes": [
                "https://api.aol.com/userinfo.profile",
                "https://api.aol.com/userinfo.email",
                "https://api.aol.com/mail.send",
            ],
            "authorization_url": "https://api.login.aol.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/5/51/AOL.svg",
        },
        "apple": {
            "scopes": ["name", "email"],
            "authorization_url": "https://appleid.apple.com/auth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
        },
        "autodesk": {
            "scopes": ["data:read", "data:write", "bucket:read", "bucket:create"],
            "authorization_url": "https://developer.api.autodesk.com/authentication/v1/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Autodesk_logo_2019.svg",
        },
        "battlenet": {
            "scopes": ["openid", "email"],
            "authorization_url": "https://oauth.battle.net/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/en/1/1b/Battle.net_Icon.svg",
        },
        "bitbucket": {
            "scopes": ["account", "email"],
            "authorization_url": "https://bitbucket.org/site/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Bitbucket-blue-logomark-only.svg",
        },
        "bitly": {
            "scopes": ["bitly:read", "bitly:write"],
            "authorization_url": "https://bitly.com/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/5/56/Bitly_logo.svg",
        },
        "clearscore": {
            "scopes": ["user.info.read", "email.send"],
            "authorization_url": "https://auth.clearscore.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/en/5/57/ClearScore_logo.png",
        },
        "cloud_foundry": {
            "scopes": ["cloud_controller.read", "openid", "email"],
            "authorization_url": "https://login.system.example.com/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Cloud_Foundry_Logo.svg/512px-Cloud_Foundry_Logo.svg.png",
        },
        "deutsche_telekom": {
            "scopes": ["t-online-profile", "t-online-email"],
            "authorization_url": "https://www.telekom.com/ssoservice/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/d/d2/Logo_telekom_2013.svg",
        },
        "deviantart": {
            "scopes": ["user", "browse", "stash", "send_message"],
            "authorization_url": "https://www.deviantart.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/b/b5/DeviantArt_Logo.svg",
        },
        "discord": {
            "scopes": ["identify", "email"],
            "authorization_url": "https://discord.com/api/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/9/98/Discord_logo.svg",
        },
        "dropbox": {
            "scopes": ["account_info.read", "files.metadata.read"],
            "authorization_url": "https://www.dropbox.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Dropbox_Icon.svg",
        },
        "facebook": {
            "scopes": ["public_profile", "email", "pages_messaging"],
            "authorization_url": "https://www.facebook.com/v10.0/dialog/oauth",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg",
        },
        "fatsecret": {
            "scopes": ["profile.get"],
            "authorization_url": "https://oauth.fatsecret.com/connect/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/en/2/20/FatSecret.png",
        },
        "fitbit": {
            "scopes": [
                "activity",
                "heartrate",
                "location",
                "nutrition",
                "profile",
                "settings",
                "sleep",
                "social",
                "weight",
            ],
            "authorization_url": "https://www.fitbit.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/6/60/Fitbit_logo_2016.svg",
        },
        "formstack": {
            "scopes": ["formstack:read", "formstack:write"],
            "authorization_url": "https://www.formstack.com/api/v2/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/en/0/09/Formstack_logo.png",
        },
        "foursquare": {
            "scopes": [],
            "authorization_url": "https://foursquare.com/oauth2/authenticate",
            "icon": "https://upload.wikimedia.org/wikipedia/en/1/12/Foursquare_logo.svg",
        },
        "github": {
            "scopes": ["user:email", "read:user"],
            "authorization_url": "https://github.com/login/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg",
        },
        "gitlab": {
            "scopes": ["read_user", "api", "email"],
            "authorization_url": "https://gitlab.com/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/1/18/GitLab_Logo.svg",
        },
        "google": {
            "scopes": [
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
            ],
            "authorization_url": "https://accounts.google.com/o/oauth2/auth",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg",
        },
        "huddle": {
            "scopes": ["user_info", "send_email"],
            "authorization_url": "https://login.huddle.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/1/1c/Huddle_logo.png",
        },
        "imgur": {
            "scopes": ["read", "write"],
            "authorization_url": "https://api.imgur.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Imgur_logo.svg",
        },
        "instagram": {
            "scopes": ["user_profile", "user_media"],
            "authorization_url": "https://api.instagram.com/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png",
        },
        "intel_cloud_services": {
            "scopes": [
                "https://api.intel.com/userinfo.read",
                "https://api.intel.com/mail.send",
            ],
            "authorization_url": "https://auth.intel.com/oauth2/v2.0/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Intel_logo_%282006-2020%29.svg",
        },
        "jive": {
            "scopes": ["user", "email"],
            "authorization_url": "https://example.jive.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Jive_Software_logo.svg",
        },
        "keycloak": {
            "scopes": ["openid", "email", "profile"],
            "authorization_url": "https://your-keycloak-server/auth/realms/your-realm/protocol/openid-connect/auth",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/0/05/Keycloak_Logo.png",
        },
        "linkedin": {
            "scopes": ["r_liteprofile", "r_emailaddress", "w_member_social"],
            "authorization_url": "https://www.linkedin.com/oauth/v2/authorization",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png",
        },
        "microsoft": {
            "scopes": [
                "https://graph.microsoft.com/User.Read",
                "https://graph.microsoft.com/Mail.Send",
                "https://graph.microsoft.com/Calendars.ReadWrite.Shared",
            ],
            "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
        },
        "netiq": {
            "scopes": ["profile", "email", "openid", "user.info"],
            "authorization_url": "https://your-netiq-domain.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/4/4d/NetIQ_logo.png",
        },
        "okta": {
            "scopes": ["openid", "profile", "email"],
            "authorization_url": "https://your-okta-domain/oauth2/v1/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Okta_logo.png",
        },
        "openam": {
            "scopes": ["profile", "email"],
            "authorization_url": "https://your-openam-base-url/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/7/7a/OpenAM_logo.png",
        },
        "openstreetmap": {
            "scopes": ["read_prefs"],
            "authorization_url": "https://www.openstreetmap.org/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/7/7e/OpenStreetMap_logo.svg",
        },
        "orcid": {
            "scopes": ["/authenticate", "/activities/update"],
            "authorization_url": "https://orcid.org/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/0/0e/ORCID_logo.png",
        },
        "paypal": {
            "scopes": ["email openid"],
            "authorization_url": "https://www.paypal.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg",
        },
        "ping_identity": {
            "scopes": ["profile", "email", "openid"],
            "authorization_url": "https://your-ping-identity-domain/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Ping_Identity_logo.png",
        },
        "pixiv": {
            "scopes": ["pixiv.scope.profile.read"],
            "authorization_url": "https://oauth.secure.pixiv.net/auth/token",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Pixiv_logo.svg",
        },
        "reddit": {
            "scopes": ["identity", "submit", "read"],
            "authorization_url": "https://www.reddit.com/api/v1/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/en/8/82/Reddit_logo_and_wordmark.svg",
        },
        "salesforce": {
            "scopes": ["refresh_token full email"],
            "authorization_url": "https://login.salesforce.com/services/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/5/51/Salesforce_logo.svg",
        },
        "sina_weibo": {
            "scopes": ["email", "statuses_update"],
            "authorization_url": "https://api.weibo.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/8/86/Sina_Weibo_logo.svg",
        },
        "spotify": {
            "scopes": ["user-read-email", "user-read-private", "playlist-read-private"],
            "authorization_url": "https://accounts.spotify.com/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.png",
        },
        "stack_exchange": {
            "scopes": ["read_inbox no_expiry private_info write_access"],
            "authorization_url": "https://stackexchange.com/oauth",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Stack_Exchange_logo.png",
        },
        "strava": {
            "scopes": ["read", "activity:write"],
            "authorization_url": "https://www.strava.com/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/2/29/Strava_Logo.png",
        },
        "stripe": {
            "scopes": ["read_write"],
            "authorization_url": "https://connect.stripe.com/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/3/30/Stripe_Logo%2C_revised_2016.png",
        },
        "twitch": {
            "scopes": ["user:read:email"],
            "authorization_url": "https://id.twitch.tv/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/9/98/Twitch_logo.svg",
        },
        "viadeo": {
            "scopes": ["basic", "email"],
            "authorization_url": "https://secure.viadeo.com/oauth-provider/authorize2",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Viadeo_logo.png",
        },
        "vimeo": {
            "scopes": ["public", "private", "video_files"],
            "authorization_url": "https://api.vimeo.com/oauth/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Vimeo_logo.png",
        },
        "vk": {
            "scopes": ["email"],
            "authorization_url": "https://oauth.vk.com/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/2/21/VK.com-logo.svg",
        },
        "wechat": {
            "scopes": ["snsapi_userinfo"],
            "authorization_url": "https://open.weixin.qq.com/connect/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/8/8e/WeChat_logo.svg",
        },
        "withings": {
            "scopes": ["user.info", "user.metrics", "user.activity"],
            "authorization_url": "https://account.withings.com/oauth2_user/authorize2",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/9/9c/Withings_logo.png",
        },
        "xero": {
            "scopes": ["openid", "profile", "email", "offline_access"],
            "authorization_url": "https://login.xero.com/identity/connect/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/5/5d/Xero_logo.svg",
        },
        "xing": {
            "scopes": [
                "https://api.xing.com/v1/users/me",
                "https://api.xing.com/v1/authorize",
            ],
            "authorization_url": "https://api.xing.com/v1/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Xing_logo.svg",
        },
        "yahoo": {
            "scopes": ["profile", "email", "mail-w"],
            "authorization_url": "https://api.login.yahoo.com/oauth2/request_auth",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/6/63/Yahoo%21_logo.svg",
        },
        "yammer": {
            "scopes": ["messages:email", "messages:post"],
            "authorization_url": "https://www.yammer.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Yammer_logo.png",
        },
        "yandex": {
            "scopes": ["login:info login:email", "mail.send"],
            "authorization_url": "https://oauth.yandex.com/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/9/96/Yandex_logo.png",
        },
        "yelp": {
            "scopes": ["business"],
            "authorization_url": "https://www.yelp.com/oauth2/authorize",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/6/62/Yelp_Logo.svg",
        },
        "zendesk": {
            "scopes": ["read", "write"],
            "authorization_url": "https://your-zendesk-domain/oauth/authorizations/new",
            "icon": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Zendesk_logo.png",
        },
    }
    return providers[provider] if provider in providers else None


def get_sso_provider(provider: str, code, redirect_uri=None):
    provider_info = get_provider_info(provider)
    if provider_info:
        return provider_info["function"](code=code, redirect_uri=redirect_uri)
    else:
        return None
