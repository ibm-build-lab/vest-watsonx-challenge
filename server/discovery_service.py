
import os
import re

import requests
from bs4 import BeautifulSoup
from flask import Blueprint

api = Blueprint('api', __name__)

CLOUD_IAM_URL = "https://iam.cloud.ibm.com/identity/token"

DISC_URL = os.getenv('WATSON_DISCOVERY_URL')
DISC_PROJ_NAME = os.getenv('WATSON_DISCOVERY_PROJECT_NAME')
DISC_PROJ_ID = os.getenv('WATSON_DISCOVERY_PROJECT_ID')
DISC_MAXIMO_DOCS = os.getenv('DISCOVERY_MAXIMO_DOCS')
DISC_MAXIMO_WEB = os.getenv('DISCOVERY_MAXIMO_WEB')
DISC_INSTANA_DOCS = os.getenv('DISCOVERY_INSTANA_DOCS')
DISC_INSTANA_WEB = os.getenv('DISCOVERY_INSTANA_WEB')
DISC_KEY = os.getenv("WATSON_DISCOVERY_API_KEY")

collection_dict = {
    'MAXIMO': [DISC_MAXIMO_DOCS, DISC_MAXIMO_WEB],
    'INSTANA': [DISC_INSTANA_DOCS, DISC_INSTANA_WEB],
    'ALL': [DISC_INSTANA_WEB, DISC_INSTANA_DOCS, DISC_MAXIMO_DOCS, DISC_MAXIMO_WEB]
}

print(DISC_PROJ_NAME)
print(DISC_MAXIMO_DOCS)
print(DISC_MAXIMO_WEB)
print(DISC_INSTANA_DOCS)
print(DISC_INSTANA_WEB)

def get_access_token():
    print("making access token request")
    r = requests.post(CLOUD_IAM_URL, data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": DISC_KEY})
    return r.json()["access_token"]

def sanitize_text(original):
    print('encoding original string: ')
    print(original, flush=True)
    string_encode = original.encode("ascii", "ignore")
    string_decode = string_encode.decode()
    cleantext = BeautifulSoup(string_decode, 'html.parser').text
    perfecttext = " ".join(cleantext.split())
    perfecttext = re.sub(' +', ' ', perfecttext).strip('"')
    return perfecttext

def query_discovery(question, product):
    token = get_access_token()
    print("received access token")

    collection_ids = collection_dict[product]
    query_url = DISC_URL + "/v2/projects/" + DISC_PROJ_ID + "/query?version=2023-03-31"
    query_body = {
        'collection_ids': collection_ids,
        'query': 'text:'+question,
        'passages': {'enabled': True, 'per_document': True}
    }

    print('query discovery documents: ' + query_url)
    print(query_body, flush=True)
    query = requests.post(query_url, json=query_body, headers={'Authorization': 'Bearer ' + token})
    
    print('Received query result')
    query_resp = query.json()
    query_results = query_resp['results']
    results_len = len(query_results)

    consolidated_text = ''
    print('Combining results: ', results_len, flush=True)
    for i in range(0, results_len):
        consolidated_text = consolidated_text + query_results[i]['document_passages'][0]['passage_text']

    sanitized_text = sanitize_text(consolidated_text)
    print('sanitized text:')
    print(sanitized_text, flush=True)
    return sanitized_text
