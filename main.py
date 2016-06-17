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

    def get_url(self, location):
        return self.url + location

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
        r = requests.post(self.get_url('auth'),
            data=payload,
            headers=headers)
        if r.status_code == 200:
            json = r.json()
            self.encryptedKey = json['encryptedKey']
            self.token = json['token']
            self.permissions = json['permissions']
            self.publicKey = ['publicKey']
            return True
        else:
            return False

    def is_authenticated(self):
        try: # If not token saved definitely not authenticated
            self.token
        except AttributeError:
            return False

        headers = {
                'Authorization': 'Bearer %s' % self.token
        }
        r = response = requests.get(
                self.get_url('auth'),
                headers=headers
        )
        if r.status_code == 200:
            return True
        else:
            return False


if __name__=='__main__':
    s = Safe('Test', '0.0.1', 'hintofbasil', 'com.github.hintofbasil')
