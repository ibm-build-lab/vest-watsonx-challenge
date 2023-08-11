import random

from discovery_service import query_discovery
from flask import Blueprint, jsonify, make_response, request
from watsonx_service import query_watsonx

api = Blueprint('api', __name__)

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

    product = request.get_json().get('product')
    if product is None or (product.upper() not in ACCEPTED_PRODUCTS):
        product = 'ALL'

    discovery_result = query_discovery(question, product)
    json_response = jsonify({"answer": discovery_result})
    return make_response(json_response, 200, RESPONSE_HEADERS)

@api.route("/watsonx/query", methods = ['POST'])
def watsonx_query():
    prompt_input = request.get_json().get('input')
    if prompt_input is None:
        return make_response('Required field "input" is missing from body', 400, RESPONSE_HEADERS)

    watsonx_result = query_watsonx(prompt_input)
    json_response = jsonify({"answer": watsonx_result})
    return make_response(json_response, 200, RESPONSE_HEADERS)

@api.route("/question", methods = ['POST'])
def question_api():    
    question = request.get_json().get('question')
    if question is None:
        return make_response('Required field "question" is missing from body', 400, RESPONSE_HEADERS)
    
    product = request.get_json().get('product')
    if product is None or (product.upper() not in ACCEPTED_PRODUCTS):
        product = 'ALL'

    article = query_discovery(question, product.upper())

    watsonx_result = query_watsonx(question, article)
    
    json_response = jsonify({"answer": watsonx_result})
    return make_response(json_response, 200, RESPONSE_HEADERS)
