from falcon import HTTPNotAcceptable, HTTPUnsupportedMediaType


class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise HTTPNotAcceptable(
                'This API only supports JSON requests.')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise HTTPUnsupportedMediaType(
                    'This API only supports JSON requests')
