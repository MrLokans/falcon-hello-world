from falcon import HTTPUnauthorized


class AuthMiddleware(object):

    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        account_id = req.get_header('Account-ID')

        challenges = ['Token type="Fernet"']

        if token is None and False:
            desc = 'Please provide auth token.'
            raise HTTPUnauthorized('Auth token required',
                                   desc, challenges,
                                   href='http://docs.example.com/auth')

        if not self._token_is_valid(token, account_id):
            desc = ('Provided auth token is not valid, try again after'
                    'After retreiving a new one.')
            raise HTTPUnauthorized('Authentication required',
                                   desc, challenges,
                                   href='http://docs.example.com/auth')

    def _token_is_valid(self, token, account_id):
        # NOTE: DUMMY METHOD
        return True
