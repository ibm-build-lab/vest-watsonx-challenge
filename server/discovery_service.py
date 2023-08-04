
import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from flask import Blueprint
from dotenv import load_dotenv
from operator import itemgetter
from utils import get_access_token

api = Blueprint('api', __name__)

CLOUD_IAM_URL = "https://iam.cloud.ibm.com/identity/token"

load_dotenv()
DISC_URL = os.getenv('WATSON_DISCOVERY_URL')
DISC_PROJ_NAME = os.getenv('WATSON_DISCOVERY_PROJECT_NAME')
DISC_PROJ_ID = os.getenv('WATSON_DISCOVERY_PROJECT_ID')
DISC_MAXIMO_DOCS = os.getenv('DISCOVERY_MAXIMO_DOCS')
DISC_MAXIMO_WEB = os.getenv('DISCOVERY_MAXIMO_WEB')
DISC_INSTANA_DOCS = os.getenv('DISCOVERY_INSTANA_DOCS')
DISC_INSTANA_WEB = os.getenv('DISCOVERY_INSTANA_WEB')
DISC_KEY = os.getenv("WATSON_DISCOVERY_API_KEY")
ENV = os.getenv("ENV")

collection_dict = {
    'MAXIMO': [DISC_MAXIMO_DOCS, DISC_MAXIMO_WEB],
    'INSTANA': [DISC_INSTANA_DOCS, DISC_INSTANA_WEB],
    'ALL': [DISC_INSTANA_WEB, DISC_INSTANA_DOCS, DISC_MAXIMO_DOCS, DISC_MAXIMO_WEB]
}

# Set up discovery_service logger instance
logger = logging.getLogger('discovery_service')
debug_level = logging.DEBUG if ENV == 'development' else logging.INFO
logger.setLevel(debug_level)
logger.addHandler(logging.StreamHandler())

def get_collection_id(token, collection_name):
    collections_url = DISC_URL + "/v2/projects/" + DISC_PROJ_ID + "/collections?version=2023-03-31"
    logger.info("Grab collection id values: " + collections_url)
    collections = requests.get(collections_url, 
                               headers={'Authorization': 'Bearer ' + token})
    resp = collections.json()

    for item in resp['collections']:
        if item['name'] == collection_name:
            collection_id = item['collection_id']
            logger.info('match found - return collection_id: ' + collection_id)
            return collection_id

    logger.warning('Collection name not found: ' + collection_name)
    return None

def sanitize_text(original):
    logger.info('Encoding original string: ')
    string_encode = original.encode("ascii", "ignore")
    string_decode = string_encode.decode()
    cleantext = BeautifulSoup(string_decode, 'html.parser').text
    perfecttext = " ".join(cleantext.split())
    perfecttext = re.sub(' +', ' ', perfecttext).strip('"')
    return perfecttext

async def query_discovery(question, product):
    product = product.upper()
    token = await get_access_token('discovery')
    if token:
        logger.info("Received access token")

        collection_ids = collection_dict[product]

        query_url = DISC_URL + "/v2/projects/" + DISC_PROJ_ID + "/query?version=2023-03-31"

        query_body = {
            'collection_ids': collection_ids,
            'query': 'text:'+question,
            'passages': {
                'enabled': True,
                'per_document': True
            }
        }

        logger.info('query discovery documents: ' + query_url)
        logger.info(query_body)
        query = requests.post(query_url, json=query_body, headers={'Authorization': 'Bearer ' + token})
        
        logger.info('Received query result')
        query_resp = query.json()
        query_results = query_resp.get("results", {})
        query_len = query_resp.get("matching_results", 0)

        consolidated_text = ''
        sanitized_text = ''
        logger.info(f"Combining results: {query_len}")
        if query_results:
            # Use this loop instead; easier to reason about than range() with list length which is inclusive
            for result in query_results:
                passage_text = ""
                passages = result.get("document_passages", []) # List
                for passage in passages:
                    passage_text = passage_text + passage.get("passage_text", "")

                consolidated_text = consolidated_text + passage_text

            sanitized_text = consolidated_text if query_len == 0 else sanitize_text(consolidated_text)
            logger.info('sanitized text:')
        else:
            sanitized_text = { "Error": "No results found.", "answer": None }
            return sanitized_text

        return { "Error": None, "answer": sanitized_text }
    else:
        logger.error("No access token.")
        return { "Error": "No access token", "answer": None }
