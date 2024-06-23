import io
import os
import time
import pyotp
import qrcode
import requests
import logging
import streamlit as st
from streamlit_js_eval import get_cookie, set_cookie
from Globals import getenv
import urllib.parse
from OAuth2Providers import get_provider_info

logging.basicConfig(
    level=getenv("LOG_LEVEL"),
    format=getenv("LOG_FORMAT"),
)

"""
Required environment variables:

- APP_NAME: Name of the application
- AGIXT_URI: URL of the MagicalAuth server
- APP_URI: URL of the application
"""


def sso_buttons():
    code = st.query_params.get("code", "")
    if isinstance(code, list):
        code = str(code[0])
    else:
        code = str(code)
    if code == "None" or code is None:
        code = ""
    with st.form("sso_form"):
        for page in os.listdir("./pages"):
            if page.endswith(".py"):
                provider = page.split(".py")[0].lower()
                client_id = getenv(f"{provider.upper()}_CLIENT_ID")
                if client_id == "":
                    continue
                provider_info = get_provider_info(provider=provider)
                if code == "" and "token" not in st.query_params:
                    magic_link_uri = getenv("APP_URI")
                    if magic_link_uri.endswith("/"):
                        magic_link_uri = magic_link_uri[:-1]
                    magic_link_uri = f"{magic_link_uri}/{provider}"
                    magic_link_uri_encoded = urllib.parse.quote(magic_link_uri)
                    client_id_encoded = urllib.parse.quote(client_id)
                    sso_uri = ""
                    scopes = provider_info["scopes"]
                    scopes = urllib.parse.quote(" ".join(scopes))
                    sso_uri = f"{provider_info['authorization_url']}?client_id={client_id_encoded}&redirect_uri={magic_link_uri_encoded}&scope={scopes}&response_type=code&access_type=offline&prompt=consent"
                    if sso_uri != "":
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            icon = provider_info["icon"]
                            if icon:
                                st.image(icon, width=40)
                        with col2:
                            if st.form_submit_button(
                                f"Continue with {provider.capitalize()}"
                            ):
                                st.markdown(
                                    f'<meta http-equiv="refresh" content="0;URL={sso_uri}">',
                                    unsafe_allow_html=True,
                                )
                                st.stop()


def get_user():
    app_name = getenv("APP_NAME")
    auth_uri = getenv("AGIXT_URI")
    if "code" in st.query_params:
        if (
            st.query_params["code"] != ""
            and st.query_params["code"] is not None
            and st.query_params["code"] != "None"
        ):
            st.session_state["code"] = st.query_params["code"]
    if "code" in st.session_state:
        code = st.session_state["code"]
        if code != "" and code is not None and code != "None":
            response = requests.post(
                f"{auth_uri}/v1/oauth2/google",
                json={"code": code, "referrer": getenv("APP_URI")},
            )
            if response.status_code == 200:
                data = response.json()
                if "detail" in data:
                    new_uri = data["detail"]
                    st.markdown(
                        f'<meta http-equiv="refresh" content="0;URL={new_uri}">',
                        unsafe_allow_html=True,
                    )
                    st.stop()
                else:
                    st.error(data)
                    st.stop()
    if "mfa_confirmed" in st.session_state:
        st.title(app_name)
        st.success("MFA token confirmed! Please check your email for the login link.")
        time.sleep(1)
        del st.session_state["mfa_confirmed"]
        st.stop()
    if "token" in st.query_params:
        if (
            st.query_params["token"] != ""
            and st.query_params["token"] is not None
            and st.query_params["token"] != "None"
        ):
            set_cookie("token", st.query_params["token"], 1)
            st.session_state["token"] = str(st.query_params["token"])
            st.query_params.clear()
    else:
        st.session_state["token"] = get_cookie("token")
    token = st.session_state["token"] if "token" in st.session_state else ""
    if token != "" and token is not None and token != "None":
        user_request = requests.get(
            f"{auth_uri}/v1/user",
            headers={"Authorization": token},
        )
        if user_request.status_code == 200:
            user = user_request.json()
            user["token"] = token
            return user
        else:
            set_cookie("token", "", 1)
    st.title(app_name)
    if "otp_uri" in st.session_state:
        hide_sidebar_style = """<style>
            [data-testid="stSidebar"] {display: none;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>"""
        st.markdown(hide_sidebar_style, unsafe_allow_html=True)
        otp_uri = st.session_state["otp_uri"]
        mfa_token = str(otp_uri).split("secret=")[1].split("&")[0]
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(otp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()
        st.write(
            "Registration successful! Please add the MFA token to your authenticator app."
        )
        with st.form("mfa_form"):
            st.image(img_bytes, caption="Scan this QR code to enable MFA")
            mfa_confirm = st.text_input(
                "Enter the MFA token from your authenticator app"
            )
            confirm_button = st.form_submit_button("Confirm MFA")
            if confirm_button:
                otp = pyotp.TOTP(mfa_token).verify(mfa_confirm)
                if otp:
                    _ = requests.post(
                        f"{auth_uri}/v1/login",
                        json={"email": st.session_state["email"], "token": mfa_confirm},
                    )
                    st.session_state["mfa_confirmed"] = True
                    if "otp_uri" in st.session_state:
                        del st.session_state["otp_uri"]
                    st.rerun()
                else:
                    st.write("Invalid MFA token. Please try again.")
                    st.stop()
    else:
        # Hide side menu
        hide_sidebar_style = """<style>
            [data-testid="stSidebar"] {display: none;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>"""
        st.markdown(hide_sidebar_style, unsafe_allow_html=True)
        new_user = st.checkbox("I am a new user")
        if not new_user:
            with st.form("login_form"):
                email = st.text_input("Email")
                otp = st.text_input("MFA Token")
                login_button = st.form_submit_button("Login")
                if login_button:
                    auth_response = requests.post(
                        f"{auth_uri}/v1/login",
                        json={
                            "email": email,
                            "token": otp,
                            "referrer": getenv("APP_URI"),
                        },
                    )
                    res = (
                        str(auth_response.json()["detail"])
                        if "detail" in auth_response.json()
                        else auth_response.json()
                    )
                    if auth_response.status_code == 200:
                        if res.startswith("http"):
                            # Redirect to the login link
                            st.markdown(
                                f'<meta http-equiv="refresh" content="0;URL={res}">',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.success(res)
                    else:
                        st.error(res)
            sso_buttons()
        else:
            with st.form("register_form"):
                email = st.text_input("Email")
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                register_button = st.form_submit_button("Register")
                if register_button:
                    # Make sure nothing is empty
                    if email == "" or first_name == "" or last_name == "":
                        st.write("Please fill out all fields.")
                        st.stop()
                    response = requests.post(
                        f"{auth_uri}/v1/user",
                        json={
                            "email": email,
                            "first_name": first_name,
                            "last_name": last_name,
                        },
                    )
                    try:
                        mfa_token = response.json()["otp_uri"]
                    except Exception as e:
                        st.write(response.json())
                        st.stop()
                    st.session_state["email"] = email
                    st.session_state["otp_uri"] = mfa_token
                    st.rerun()
    st.stop()


def log_out_button():
    token = get_cookie("token", "logout_token")
    if token != "":
        if st.button("Log Out"):
            set_cookie("token", "", 1, "logout_set_token")
            st.query_params.clear()
            st.session_state["token"] = ""
            st.success("You have been logged out. Redirecting to login page...")
            st.markdown(
                f'<meta http-equiv="refresh" content="2;URL=/">',
                unsafe_allow_html=True,
            )
            time.sleep(2)
            st.stop()


def sso_redirect(provider: str):
    auth_uri = getenv("AGIXT_URI")
    if "code" in st.query_params:
        if (
            st.query_params["code"] != ""
            and st.query_params["code"] is not None
            and st.query_params["code"] != "None"
        ):
            st.session_state["code"] = st.query_params["code"]
    if "code" in st.session_state:
        code = st.session_state["code"]
        if code != "" and code is not None and code != "None":
            referrer = f"{getenv('APP_URI')}/{provider}"
            response = requests.post(
                f"{auth_uri}/v1/oauth2/{provider}",
                json={"code": code, "referrer": referrer},
            )
            if response.status_code == 200:
                data = response.json()
                if "detail" in data:
                    new_uri = data["detail"]
                    st.markdown(
                        f'<meta http-equiv="refresh" content="0;URL={new_uri}">',
                        unsafe_allow_html=True,
                    )
                    st.stop()
                else:
                    st.error(data)
                    st.stop()
    if "token" in st.query_params:
        if (
            st.query_params["token"] != ""
            and st.query_params["token"] is not None
            and st.query_params["token"] != "None"
        ):
            get_user()
    if "token" not in st.query_params and "code" not in st.query_params:
        # Reload to ../ page
        st.markdown(
            f'<meta http-equiv="refresh" content="1;URL=../">',
            unsafe_allow_html=True,
        )


def hide_pages():
    dont_show_pages = [
        "amazon",
        "aol",
        "apple",
        "autodesk",
        "battlenet",
        "bitbucket",
        "bitly",
        "clearscore",
        "cloud_foundry",
        "deutsche_telekom",
        "deviantart",
        "discord",
        "dropbox",
        "facebook",
        "fatsecret",
        "fitbit",
        "formstack",
        "foursquare",
        "github",
        "gitlab",
        "google",
        "huddle",
        "imgur",
        "instagram",
        "intel_cloud_services",
        "jive",
        "keycloak",
        "linkedin",
        "microsoft",
        "netiq",
        "okta",
        "openam",
        "openstreetmap",
        "orcid",
        "paypal",
        "ping_identity",
        "pixiv",
        "reddit",
        "salesforce",
        "sina_weibo",
        "spotify",
        "stack_exchange",
        "strava",
        "stripe",
        "twitch",
        "viadeo",
        "vimeo",
        "vk",
        "wechat",
        "withings",
        "xero",
        "xing",
        "yahoo",
        "yammer",
        "yandex",
        "yelp",
        "zendesk",
    ]
    hide_pages_style = """
    <style>
    """
    for page in dont_show_pages:
        hide_pages_style += f'[data-testid="stSidebar"] ul li:has(a[href*="{page}"]) {{display: none;}}\n'
    hide_pages_style += """
    </style>
    """
    # Apply the custom CSS
    st.markdown(hide_pages_style, unsafe_allow_html=True)
