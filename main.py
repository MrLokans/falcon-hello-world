import json
import logging
import uuid

from wsgiref import simple_server

import falcon
import requests


from middleware import (
    AuthMiddleware,
)


class StorageEngine(object):

    def get_things(self, marker, limit):
        return [{'id': self.generate_uuid(), 'color': 'green'}]

    def add_thing(self, thing):
        thing['id'] = self.generate_uuid()
        return thing

    @classmethod
    def generate_uuid(cls):
        return str(uuid.uuid4())


class StorageError(Exception):

    @staticmethod
    def handle(ex, req, resp, params):
        desc = ('Sorry, couldn\'t write your thing to the '
                'database.')
        raise falcon.HTTPError(falcon.HTTP_725,
                               'Database Error',
                               desc)


class SinkAdapter(object):

    engines = {
        'ddg': 'https://duckduckgo.com',
        'y': 'https://search.yahoo.com/search',
    }

    def __call__(self, req, resp, engine):
        url = self.engines.get(engine, 'ddg')
        params = {'q': req.get_param('q', True)}
        result = requests.get(url, params=params)

        resp.status = " ".join([result.status_code, result.reason])
        resp.content_type = result.headers['content-type']
        resp.body = result.text

app = falcon.API(middleware=[
    AuthMiddleware(),
])

db = StorageEngine()

# If StorageError is raised corresponding handler is used
app.add_error_handler(StorageError, StorageError.handle)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8181, app)
    httpd.serve_forever()
