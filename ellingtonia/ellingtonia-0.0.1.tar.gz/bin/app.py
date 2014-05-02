import os
import sys

from flask import Flask
from flask import render_template


app = Flask(__name__)

def get_context():
    base_path = 'docs_target'
    clients = []

    for client_name in os.listdir(base_path):
        client = {
            "name": client_name,
            "projects": []
        }
        projects = []
        project_path = os.path.join(base_path, client_name)
        for project in os.listdir(project_path):
            client['projects'].append({
                'name': project,
                'url': "%s/%s/index.html" % (project_path, project)
            })
        clients.append(client)
    return clients



@app.route('/')
def hello():
    return render_template(
        'index.html',
        clients=get_context()
    )



if __name__ == '__main__':
    app.run(debug= True)