from utils import Logger

from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS, cross_origin
import logging
import threading
from datetime import datetime
from time import sleep
import webbrowser
import json

tokens = []

logger = Logger()


def manageTokens():
    while True:
        for token in tokens:
            if token['expiry'] < datetime.now().timestamp():
                tokens.remove(token)
                logger.error("Token expired and deleted")
        sleep(5)


def sendToken():
    while not tokens:
        pass
    token = tokens.pop(0)
    return token['token']


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
@cross_origin()
def index():
    return render_template('index.html', sitekey=config['sitekey'], domain=config['domain'])


@app.route('/api/submit', methods=['POST'])
@cross_origin()
def submit():
    try:
        token = request.form['g-recaptcha-response']
        expiry = datetime.now().timestamp() + 115
        tokenDict = {
            'token': token,
            'expiry': expiry
        }
        tokens.append(tokenDict)
        logger.success("Token harvested and stored")
        return jsonify({
            'success': True,
            'error': None,
            'result': 'Token harvested and stored'
        })
    except:
        return jsonify({
            'success': False,
            'error': 'Undocumented error',
            'result': None
        })


@app.route('/api/count')
@cross_origin()
def api_count():
    return jsonify({
        'success': True,
        'error': None,
        'result': len(tokens)
    })


@app.route('/api/token')
@cross_origin()
def api_fetch_token():
    try:
        token = tokens.pop(0)
        logger.status("Token requested and returned to user")
        return jsonify({
            'success': True,
            'error': None,
            'result': token['token']
        })
    except:
        logger.warn("Token requested but none available")
        return jsonify({
            'success': False,
            'error': 'Token requested but none available',
            'result': None
        })


if __name__ == '__main__':
    threading.Thread(target=manageTokens).start()
    with open('config.json') as file:
        config = json.load(file)
        file.close()
    logger.log("*****************************************************")
    logger.log("CSGORoll reCAPTCHA Harvester | blic blic")
    logger.log("*****************************************************")
    logger.log("Server running at harvester.{}:5000".format(config['domain']))
    webbrowser.open('http://harvester.{}:5000/'.format(config['domain']))
    app.run()
