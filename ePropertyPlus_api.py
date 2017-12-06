### This is a helper class for accessing the ePropertyPlus API.
### Written by Chris Hartley, Renew Indianapolis
### (c) 2017 Released under the GNU Public License v3

class ePPHelper(object):

    def __init__(self, key, endpoint):
        self.api_key = key
        self.endpoint = endpoint
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (ePPHelper Class)',
            'Content-Type': 'application/json',
            'x-strllc-authkey':  key,
            'Accept': 'application/json',
        }

    def query(self, api_resource, json_query):
        url = '{0}{1}'.format(self.endpoint, api_resource,)

        parameters = {
            'page': 1,
            'limit': 50000, 
            'json': json_query,
        }
        s = Session()
        s.headers.update(self.headers)
        r = s.post(url, params=parameters)
        return r.json()
