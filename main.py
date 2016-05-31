import logging

from wsgiref import simple_server

import falcon
import requests


from conf import DEFAULT_LIMIT
from middleware import (
    AuthMiddleware,
    JSONTranslator,
    RequireJSON
)
from storage import StorageError, StorageEngine


class SinkAdapter(object):

    engines = {
        'ddg': 'https://duckduckgo.com',
        'y': 'https://search.yahoo.com/search',
    }

    def __call__(self, req, resp, engine):
        url = self.engines.get(engine, 'ddg')
        params = {'q': req.get_param('q', True)}
        result = requests.get(url, params=params)

        resp.status = " ".join([str(result.status_code), str(result.reason)])
        resp.content_type = result.headers['content-type']
        resp.body = result.text


def max_body(limit):

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class ThingsResource(object):

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger('falconhello.' + __name__)

    def on_get(self, req, resp, user_id):
        marker = req.get_param('marker') or ''
        limit = req.get_param_as_int('limit') or DEFAULT_LIMIT

        try:
            result = self.db.get_things(marker, limit)
        except Exception as e:
            self.logger.error(e)

            msg = 'Unknown error occured with us'
            raise falcon.HTTPServiceUnavailable(
                'Service unavailable',
                msg,
                30)

        # This will go throug JSON translator middleware
        req.context['result'] = result

        resp.set_header('Powered-By', 'Falcon')
        resp.status = falcon.HTTP_200

    @falcon.before(max_body(64 * 1024))
    def on_post(self, req, resp, user_id):
        try:
            doc = req.context['doc']
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Missing thing',
                'A thing must be submitted in the request body.')

        proper_thing = self.db.add_thing(doc)

        resp.status = falcon.HTTP_201
        resp.location = '/%s/things/%s' % (user_id, proper_thing['id'])


app = falcon.API(middleware=[
    AuthMiddleware(),
    JSONTranslator(),
    RequireJSON(),
])

db = StorageEngine()
things = ThingsResource(db)
app.add_route('/{user_id}/things', things)

# If StorageError is raised corresponding handler is used
app.add_error_handler(StorageError, StorageError.handle)

# Requests are being processed by another service
sink = SinkAdapter()
app.add_sink(sink, r'/search/(?P<engine>ddg|y)\Z')

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8181, app)
    httpd.serve_forever()
