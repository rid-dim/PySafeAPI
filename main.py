#!/usr/bin/env python

from nacl.public import PrivateKey, Box
import nacl.utils
import requests
import base64

class Safe:

    def __init__(self,
            name,
            version,
            vendor,
            id,
            addr='http://localhost',
            port=8100):
        self.name = name
        self.version = version
        self.vendor = vendor
        self.id = id
        self.url = "%s:%d/" % (addr, port)

    def authenticate(self, permissions=[]): #TODO check is needs to = None
        keys = PrivateKey.generate()
        nonce = nacl.utils.random(Box.NONCE_SIZE)
        payload = {
            'app': {
                'name': self.name,
                'version': self.version,
                'vendor': self.vendor,
                'id': self.id
            },
            'publicKey': base64.b64encode(keys.public_key.__bytes__()),
            'nonce': base64.b64encode(nonce),
            'permissions': permissions
        }
        headers = {
            'Content-Type': 'application/json'
        }
        # Requires use to " instead of '
        # TODO handle quotes in parameters
        payload = str(payload).replace('\'', '"')
        r = requests.post('http://localhost:8100/auth',
            data=payload,
            headers=headers)
        print r.text

if __name__=='__main__':
    s = Safe('Test', '0.0.1', 'hintofbasil', 'com.github.hintofbasil')
    s.authenticate()
