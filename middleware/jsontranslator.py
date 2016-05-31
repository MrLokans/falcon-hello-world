import json

from falcon import HTTPBadRequest, HTTPError, HTTP_753


class JSONTranslator(object):

    def process_request(self, req, resp):
        """req.stream corresponds to the WSGI wsgi.input environ variable,
        and allows you to read bytes from the request body."""

        if req.content_length in (None, 0):
            return

        body = req.stream.read()
        if not body:
            raise HTTPBadRequest('Empty request body',
                                 'Invalid JSON sent')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            msg = 'Malformed JSON: incorrect JSON or not encoded as UTF-8'
            raise HTTPError(HTTP_753, msg)

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return
        resp.body = json.dumps(req.context['result'])
