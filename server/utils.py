import json
import logging
import requests
from os import getenv
from dotenv import load_dotenv

load_dotenv()
ENV = getenv("ENV")
DISC_KEY = getenv("WATSON_DISCOVERY_API_KEY")
WATSONX_CLOUD_API_KEY = getenv("WATSONX_CLOUD_API_KEY")
CLOUD_IAM_URL = "https://iam.cloud.ibm.com/identity/token"

service_map = {
    'discovery': DISC_KEY,
    'watsonx': WATSONX_CLOUD_API_KEY
}

# Set up Utils logger instance
logger = logging.getLogger('utils')
debug_level = logging.DEBUG if ENV == 'development' else logging.INFO
logger.setLevel(debug_level)
logger.addHandler(logging.StreamHandler())

# Useful to debug: pretty print JSON logging
def pretty_json(input):
    return json.dumps(input, indent=2)

async def get_access_token(service):
    logger.info("Making access token request")
    try:
        r = requests.post(CLOUD_IAM_URL, data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": service_map[service]})
        return r.json()["access_token"]
    except Exception as e:
        logger.error(e)
        return False
