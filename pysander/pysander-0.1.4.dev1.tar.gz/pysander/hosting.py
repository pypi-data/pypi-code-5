import flask
import functools
import auth
import context
import queries
import validation

# Context extension that adds http requests to the pysander context object

class HTTPContext(object):
    def __init__(self):
        self.request = None

    def enter(self):
        self.request = flask.request

    def get_request(self):
        return self.request

# Composes an array of python function decorators into a single decorator

def compose_decorators(*decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco

# Creates a decorator which creates a pysander context to wrap a function call with

def with_context(factory):
    def deco(f):
        def wrapper(*args, **kwargs):
            with factory.create_context():
                return f(*args, **kwargs)
        return functools.update_wrapper(wrapper, f)
    return deco

# Handles returning responses from actions as JSON responses

def with_json_response():
    def deco(f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            return flask.Response(flask.json.dumps(result),  mimetype='application/json')
        return functools.update_wrapper(wrapper, f)
    return deco

# Hosts a set of repositories on a flask application

class RepositoryHoster(object):
    def __init__(self):
        self.decorators = []
        self.repositories = {}

    def add_decorator(self, decorator):
        self.decorators.append(decorator)

    def add_repository(self, name, repo):
        self.repositories[name] = repo

    def get_composed_decorator(self):
        return compose_decorators(*self.decorators)

    def host(self, app, prefix=''):

        @app.route(prefix + '/<repo>/<id>', methods=['GET'], endpoint='pysander_find')
        @self.get_composed_decorator()
        def find(repo, id):
            repo = self.repositories[repo]
            return repo.find(id)

        @app.route(prefix + '/<repo>/query', methods=['POST'], endpoint='pysander_query')
        @self.get_composed_decorator()
        def query(repo):
            json = context.current().get_request().get_json()
            query = queries.from_json(json)
            repo = self.repositories[repo]
            return repo.query(query)

        @app.route(prefix + '/<repo>/count', methods=['POST'], endpoint='pysander_count')
        @self.get_composed_decorator()
        def count(repo):
            json = context.current().get_request().get_json()
            query = queries.from_json(json)
            repo = self.repositories[repo]
            return repo.count(query)

        @app.route(prefix + '/<repo>/insert', methods=['POST'], endpoint='pysander_insert')
        @self.get_composed_decorator()
        def insert(repo):
            repo = self.repositories[repo]
            json = context.current().get_request().get_json()
            key = repo.insert(json)
            return repo.find(key)

        @app.route(prefix + '/<repo>/<id>', methods=['PATCH'], endpoint='pysander_update')
        @self.get_composed_decorator()
        def update(repo, id):
            repo = self.repositories[repo]
            json = context.current().get_request().get_json()
            repo.update(id, json)
            return repo.find(id)

        @app.route(prefix + '/<repo>/<id>', methods=['DELETE'], endpoint='pysander_delete')
        @self.get_composed_decorator()
        def delete(repo, id):
            repo = self.repositories[repo]
            return repo.delete(id)

        @app.route(prefix + '/<repo>/changeset', methods=['POST'], endpoint='pysander_changeset')
        @self.get_composed_decorator()
        def changeset(repo):
            repo = self.repositories[repo]
            json = context.current().get_request().get_json()
            deletions = json['delete']
            updates = json['update']
            insertions = json['insert']
            for deletion in deletions:
                id = deletion['id']
                repo.delete(id)
            for update in updates:
                id = update['id']
                repo.update(id, update)
            for insertion in insertions:
                repo.insert(insertion)
            return {
                'deletions' : len(deletions),
                'updates' : len(updates),
                'insertions' : len(insertions)
            }
