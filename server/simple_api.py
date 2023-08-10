import random
from flask import jsonify, make_response, request, Blueprint
from discovery_service import query_discovery

api = Blueprint('api', __name__)

ACCEPTED_PRODUCTS = ['MAXIMO', 'INSTANA']

@api.route("/rand", methods = ['GET'])
def random_num():
    """Simple REST API example to be called from frontend"""
    headers = { "Content-Type": "application/json" }
    data = { "num": random.randint(0, 100) }
    return make_response(jsonify(data), 200, headers)

@api.route("/hello_get", methods = ['GET'])
def hello_get():
    """Simple REST API that can parse URL params"""
    headers = { "Content-Type": "application/json" }

    name = request.args.get('name')
    if name is None:
        return make_response('Error no name param in URL', 400, headers)

    return make_response(f"Hello, {name}!", 200, headers)

@api.route("/hello_post", methods = ['POST'])
def hello_post():
    """Simple REST API that can parse JSON body in request"""
    headers = { "Content-Type": "application/json" }
    
    name = request.get_json().get('name')
    if name is None:
        return make_response('Error no name param in request body', 400, headers)

    return make_response(f"Hello, {name}!", 200, headers)

@api.route("/discovery/query", methods = ['POST'])
def discovery_query():
    headers = { "Content-Type": "application/json" }
    
    question = request.get_json().get('question')
    if question is None:
        return make_response('Required field "question" is missing from body', 400, headers)

    product = request.get_json().get('product')
    if product is None or (product.upper() not in ACCEPTED_PRODUCTS):
        product = 'ALL'

    discovery_result = query_discovery(question, product)
    json_response = jsonify({"answer": discovery_result})
    return make_response(json_response, 200, headers)

@api.route("/question", methods = ['POST'])
def question_api():
    headers = { "Content-Type": "application/json" }
    
    question = request.get_json().get('question')
    if question is None:
        return make_response('Required field "question" is missing from body', 400, headers)
    
    product = request.get_json().get('product')
    if product is None or (product.upper() not in ACCEPTED_PRODUCTS):
        product = 'ALL'

    article = query_discovery(question, product.upper())

    # watsonx_result = query_watsonx(question, article)
    # TODO: Replce article response with watsonx_result once watsonx service is available
    json_response = jsonify({"answer": article})
    return make_response(json_response, 200, headers)
