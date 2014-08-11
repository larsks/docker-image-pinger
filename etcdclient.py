import requests
import json


def wrap404(f):
    def _(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.HTTPError, detail:
            if detail.response.status_code == 404:
                raise KeyError()
            raise

    return _

class Etcd(object):
    def __init__(self, endpoint='http://localhost:4001/v2'):
        self.endpoint = endpoint

    def set(self, key, value, ttl=None):
        uri = '%s/keys/%s' % (self.endpoint, key)
        data = {'value': value}
        if ttl is not None:
            data['ttl'] = ttl

        res = requests.put(uri, data=data)
        res.raise_for_status()
        return res.json()

    def append(self, key, value, ttl=None):
        uri = '%s/keys/%s' % (self.endpoint, key)
        data = {'value': value}
        if ttl is not None:
            data['ttl'] = ttl

        res = requests.post(uri, data=data)
        res.raise_for_status()
        return res.json()

    def mkdir(self, key, ttl=None):
        uri = '%s/keys/%s' % (self.endpoint, key)
        data = {'dir': True}
        if ttl is not None:
            data['ttl'] = ttl

        res = requests.put(uri, data=data)
        res.raise_for_status()
        return res.json()

    @wrap404
    def rmdir(self, key, recursive=False):
        uri = '%s/keys/%s?dir=true&recursive=%s' % (
            self.endpoint, key,
            'true' if recursive else 'false',
        )
        res = requests.delete(uri)

        res.raise_for_status()
        return res.json()

    @wrap404
    def get(self, key, wait=False):
        uri = '%s/keys/%s?wait=%s' % (
            self.endpoint,
            key,
            'true' if wait else 'false',
        )
        res = requests.get(uri)
        res.raise_for_status()
        return res.json()

    @wrap404
    def get_all(self, key):
        uri = '%s/keys/%s' % (self.endpoint, key)
        res = requests.get(uri)
        res.raise_for_status()
        data = res.json()

        return data['node'].get('nodes', [])

    @wrap404
    def delete(self, key):
        uri = '%s/keys/%s' % (self.endpoint, key)
        res = requests.delete(uri)
        res.raise_for_status()
        return res.json()


if __name__ == '__main__':
    c = Etcd()

