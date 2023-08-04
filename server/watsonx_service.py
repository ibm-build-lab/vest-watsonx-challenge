import json
import requests
from os import getenv
from flask import Blueprint
from dotenv import load_dotenv
from utils import get_access_token
from logging import getLogger, DEBUG, INFO, StreamHandler

api = Blueprint('api', __name__)

WATSONX_BAM_URL = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"

CLOUD_IAM_URL = "https://iam.cloud.ibm.com/identity/token"

load_dotenv()
WATSONX_CLOUD_API_KEY = getenv("WATSONX_CLOUD_API_KEY")
WATSONX_PROJECT_ID = getenv("WATSONX_PROJECT_ID")
ENV = getenv("ENV")

HEADERS = {
  'accept': 'application/json',
  'content-type': 'application/json',
  'Authorization': 'Bearer '
}

# Set up logger.
logger = getLogger('watsonx_service') 
debug_level = DEBUG if ENV == 'development' else INFO
logger.setLevel(debug_level)
logger.addHandler(StreamHandler())

def structure_prompt(question, article):
  prompt_init = "Answer the following question using only information from the article. If there is no good answer in the article, say \"I don't know\"."
  structured_query = f"{prompt_init}\n\nArticle:\n###{article}\n###\n\nQuestion:\n{question}\n\nAnswer:\n"
  return structured_query


async def query_watsonx(question, article, max_new_tokens = 20, min_new_tokens = 0, project_id = WATSONX_PROJECT_ID, access_token = None):
  prompt = structure_prompt(question, article)
  if access_token is None:
      access_token = await get_access_token('watsonx')

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

  status = response.status_code
  if status == 200:
    watsonx_output = response.json()['results'][0]['generated_text']
    return { "answer": watsonx_output, "Error": None }
  else:
     return { "Error": json.loads(response.text).get("errors", [{}])[0].get("message", "An error occurred. Please try again.") }
