from flask import Flask, request, send_from_directory, jsonify, json
import os
import requests
import cell_acceptance
import tempfile
from flask_cors import cross_origin

app = Flask(__name__)

file_cache = {}

@app.route('/', methods=['POST', 'GET'])
@cross_origin(headers=['Content-Type'])
def run_calc():
    info = request.get_json()
    url = info['url']
    if url in file_cache:
        target = file_cache[url]
    else:
        target = tempfile.NamedTemporaryFile()
        r = requests.get(url)
        target.write(r.content)
        file_cache[url] = target
    result = cell_acceptance.calc(
        target.name,
        info['inputs'],
        info['results']
    )
    return json.dumps(result)

LOCAL = os.path.dirname(os.path.abspath(__file__))
@app.route('/files/<path:filename>')
def send_file(filename):
    return send_from_directory('%s/tests' % LOCAL, filename)

def run_server():
    app.run(debug=True)
