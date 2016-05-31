import uuid

from falcon import HTTPError, HTTP_725


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
        raise HTTPError(HTTP_725,
                        'Database Error',
                        desc)
