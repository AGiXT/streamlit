import os, requests, json
from dotenv import load_dotenv
from agixtsdk import AGiXTSDK
    
def load_env():
    f = open("server_conf.json")
    data = json.load(f)
    #st.warning(data['SERVER_URI'])
    base_uri = data['SERVER_URI']
    if base_uri[-1] == "/": base_uri=base_uri[:-1]
    api_key = data['API_KEY']
    return base_uri,api_key

if os.path.isfile("server_conf.json") == False:
    load_dotenv()
    base_uri = os.getenv("AGIXT_URI", "http://localhost:7437")
    api_key = os.getenv("AGIXT_API_KEY", "")
else:
    base_uri, api_key = load_env()

def check_server_conf(base_uri="127.0.0.1:7437/", api_key=""):
    #st.warning("Base Uri: " + base_uri)
    #st.warning("API Key: " + api_key)
    
    if os.path.isfile("server_conf.json") == False:
      print("Server Config Does Not Exist")
      if base_uri[-1] == "/": base_uri=base_uri[:-1]
      server_response = requests.get(f"{base_uri}/api/providers", headers={"Authorization": api_key})
    elif os.path.isfile("server_conf.json") == True:
      print("Server Config Found")
      load_env()
      server_response = requests.get(f"{base_uri}/api/providers", headers={"Authorization": api_key})

    try:
      return int(server_response.status_code)
    except:
      return 401
  
serv_resp = check_server_conf(base_uri, api_key)
if serv_resp == 200: 
    os.environ["AGIXT_URI"] = base_uri
    os.environ["AGIXT_API_KEY"] = api_key

if serv_resp != 200:
    # Show API config
    #st.warning(serv_resp)
    #st.warning("The API Config Is Invalid - Please Re-Enter Server URL & API Key")
    s_URI = st.text_input("Server URL:", value = base_uri, key="server_URI")
    s_KEY = st.text_input("Server API Key:", key="server_KEY")
    if st.button("Submit"):
        output_json = {"SERVER_URI" : s_URI,"API_KEY" : s_KEY}
        with open("server_conf.json", "w") as outfile:
            json.dump(output_json, outfile)
        st.rerun()
    st.stop()
    
load_dotenv()
base_uri = os.getenv("AGIXT_URI", "http://localhost:7437")
agixt_api_key = os.getenv("AGIXT_API_KEY", "")
    
ApiClient = AGiXTSDK(base_uri=base_uri, api_key=agixt_api_key)

DEV_MODE = os.getenv("DEV_MODE", False)
