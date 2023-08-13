"""Module containing simple REST Flask server."""
import os
from logging import getLogger, DEBUG, INFO, StreamHandler
from operator import itemgetter
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from simple_api import api

DEFAULT_VALUES = {
    # https://stackoverflow.com/questions/72795799/how-to-solve-403-error-with-flask-in-python
    'PORT': 5001,
    'ENV': 'development',
    'HOST': '0.0.0.0'
}

# access environment variables
load_dotenv()
PORT, ENV, HOST = itemgetter('PORT', 'ENV', 'HOST')({ **DEFAULT_VALUES, **dict(os.environ) })

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

@app.route("/", methods = ['GET'])
def index():
    """Path for returning index file"""
    return send_from_directory('../client/dist', 'index.html')

@app.route("/<path:path>")
def other(path):
    """Path for all other static files"""
    return send_from_directory('../client/dist', path)


if __name__ == "__main__":
    # Set up logger.
    logger = getLogger('server') 
    debug_level = DEBUG if ENV == 'development' else INFO
    logger.setLevel(debug_level)
    logger.addHandler(StreamHandler())

    if ENV == 'development':
        logger.info('Start Flask server in DEV mode')
        app.run(debug=True, port=PORT)
    else:
        logger.info('Starting Flask server in PROD mode')
        from waitress import serve
        serve(app, host=HOST, port=PORT)
