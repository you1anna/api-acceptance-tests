import requests
from pprint import pprint
import os


class ApiClient:
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.session = requests.Session()

    def request(self, method, url, **kwargs):
        return self.session.request(method, self.base_url + url, **kwargs)

    def get(self, url='', **kwargs):
        r = self.session.get(self.base_url + url, **kwargs)
        pprint(r.text)
        return r

    def post(self, url='', **kwargs):
        r = self.session.post(self.base_url + url, **kwargs)
        pprint(r.text)
        return r

    def put(self, url='', **kwargs):
        return self.session.put(self.base_url + url, **kwargs)

    def data(self, file=None):
        data = 'data_{}.json'.format(file)
        return open(os.path.join('tests', data), 'rb').read()
