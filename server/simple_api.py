import random
import logging
from os import getenv
from dotenv import load_dotenv
from flask import jsonify, make_response, request, Blueprint
from discovery_service import query_discovery
from watsonx_service import query_watsonx

api = Blueprint('api', __name__)

load_dotenv()

ENV = getenv("ENV")

# Set up simple_api logger instance
logger = logging.getLogger('simple_api')
debug_level = logging.DEBUG if ENV == 'development' else logging.INFO
logger.setLevel(debug_level)
logger.addHandler(logging.StreamHandler())

ACCEPTED_PRODUCTS = ['MAXIMO', 'INSTANA']
RESPONSE_HEADERS = { "Content-Type": "application/json" }

@api.route("/rand", methods = ['GET'])
def random_num():
    """Simple REST API example to be called from frontend"""
    data = { "num": random.randint(0, 100) }
    return make_response(jsonify(data), 200, RESPONSE_HEADERS)

@api.route("/hello_get", methods = ['GET'])
def hello_get():
    """Simple REST API that can parse URL params"""
    name = request.args.get('name')
    if name is None:
        return make_response('Error no name param in URL', 400, RESPONSE_HEADERS)

    return make_response(f"Hello, {name}!", 200, RESPONSE_HEADERS)

@api.route("/hello_post", methods = ['POST'])
def hello_post():
    """Simple REST API that can parse JSON body in request"""    
    name = request.get_json().get('name')
    if name is None:
        return make_response('Error no name param in request body', 400, RESPONSE_HEADERS)

    return make_response(f"Hello, {name}!", 200, RESPONSE_HEADERS)

@api.route("/discovery/query", methods = ['POST'])
def discovery_query():    
    question = request.get_json().get('question')
    if question is None:
        return make_response('Required field "question" is missing from body', 400, RESPONSE_HEADERS)

    product = request.get_json().get('product', '').upper()
    if product == '' or (product not in ACCEPTED_PRODUCTS):
        product = 'ALL'

    discovery_result = query_discovery(question, product)
    json_response = jsonify({"answer": discovery_result})
    return make_response(json_response, 200, RESPONSE_HEADERS)

@api.route("/watsonx/query", methods = ['POST'])
async def watsonx_query():
    prompt_input = request.get_json().get('input')
    if prompt_input is None:
        return make_response('Required field "input" is missing from body', 400, RESPONSE_HEADERS)

    watsonx_result = await query_watsonx(prompt_input) # Object with Error and answer
    err = watsonx_result.get("Error")
    json_response = jsonify(watsonx_result)
    if not err:
        code = 200
    else:
        code = 500

    return make_response(json_response, code, RESPONSE_HEADERS)

@api.route("/question", methods = ['POST'])
async def question_api():    
    question = request.get_json().get('question')
    if question is None:
        return make_response('Required field "question" is missing from body', 400, RESPONSE_HEADERS)
    
    product = request.get_json().get('product', '').upper()
    if product == '' or (product not in ACCEPTED_PRODUCTS):
        product = 'ALL'

    final_resp = await make_queries(question, product)
    return make_response(jsonify(final_resp), 200, RESPONSE_HEADERS)

# Helper in order to not duplicate for slack service.
async def make_queries(question, product):
    logger.info(f"Question for product {product}: {question}")
    article = await query_discovery(question, product.upper())
    err = article.get("Error")
    answer = article.get("answer")

    if not err:
        watsonx_result = await query_watsonx(question, answer)
        err = watsonx_result.get("Error")
        watson_answer = watsonx_result.get("answer")
    else:
        watson_answer = None
        # Remove possible secrets
        err = err.replace('ServiceId-d2e8ff26-aaea-41ce-a5dc-d79b9fa0c1ae', '')
        err = err.replace('3e1ef053-86f6-4bff-8320-69f930905f01', '')
    
    resp = { "answer": watson_answer, "Error": err }
    return resp
