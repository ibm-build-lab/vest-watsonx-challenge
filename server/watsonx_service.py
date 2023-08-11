import json
import os

import requests
from flask import Blueprint

api = Blueprint('api', __name__)

WATSONX_BAM_URL = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"

CLOUD_IAM_URL = "https://iam.cloud.ibm.com/identity/token"

WATSONX_CLOUD_API_KEY = os.getenv("WATSONX_CLOUD_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

HEADERS = {
  'accept': 'application/json',
  'content-type': 'application/json',
  'Authorization': 'Bearer '
}

def get_access_token():
    print("requesting access token")
    r = requests.post(CLOUD_IAM_URL, data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": WATSONX_CLOUD_API_KEY})
    return r.json()["access_token"]

def structure_prompt(question, article):
  prompt_init = "Answer the following question using only information from the article. If there is no good answer in the article, say \"I don't know\"."
  structured_query = f"{prompt_init}\n\nArticle:\n###{article}\n###\n\nQuestion:\n{question}\n\nAnswer:\n"
  return structured_query


def query_watsonx(question, article, max_new_tokens = 20, min_new_tokens = 0, project_id = WATSONX_PROJECT_ID, access_token = None):
  prompt = structure_prompt(question, article)
  if access_token is None:
      access_token = get_access_token()

  prompt_input = prompt.replace("\n", "\\n")
  headers_with_token = HEADERS.copy()
  headers_with_token['Authorization'] = 'Bearer {}'.format(access_token)
  data = {
      "model_id": "google/flan-ul2",
      "input": prompt_input,
      "parameters": {
          "decoding_method": "greedy",
          "max_new_tokens": max_new_tokens,
          "min_new_tokens": min_new_tokens,
          "stop_sequences": [],
          "repetition_penalty": 1
      },
      "project_id": project_id
  }

  try :
    response = requests.post(WATSONX_BAM_URL, headers=headers_with_token, data=json.dumps(data))
  except Exception as e:
     print("Error querying watsonx service")
     print(f'caught {type(e)} with nested {e.exceptions}')
   
  watsonx_output = response.json()['results'][0]['generated_text']
  return watsonx_output
   
