#!/usr/bin/env python

from nacl.public import PrivateKey, Box, PublicKey
from nacl.bindings.crypto_box import (crypto_box_afternm,
        crypto_box_open_afternm)
import nacl.utils
import requests
import base64
import json
import urllib

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

    def _get_url(self, location):
        return self.url + location

    def _post(self, path, headers, payload):
        url = self._get_url(path)
        payload = json.dumps(payload)
        r = requests.post(url,
            data=payload,
            headers=headers)
        return r

    def _post_encrypted(self, path, headers, payload):
        url = self._get_url(path)
        payload = json.dumps(payload)
        encryptedData = crypto_box_afternm(payload, self.symmetricNonce,
                self.symmetricKey)
        payload = base64.b64encode(encryptedData)
        r = requests.post(url,
            data=payload,
            headers=headers)
        return r

    def _put_encrypted(self, path, headers, payload):
        url = self._get_url(path)
        encryptedData = crypto_box_afternm(payload, self.symmetricNonce,
                self.symmetricKey)
        payload = base64.b64encode(encryptedData)
        r = requests.put(url,
            data=payload,
            headers=headers)
        return r

    def _decrypt_response(self, message, is_json=True):
        message = crypto_box_open_afternm(base64.b64decode(message),
                self.symmetricNonce, self.symmetricKey)
        if is_json:
            message = json.loads(message)
        return message

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
        r = self._post('auth', headers, payload)
        if r.status_code == 200:
            responseJson = r.json()
            cipherText = base64.b64decode(responseJson['encryptedKey'])
            self.token = responseJson['token']
            self.permissions = responseJson['permissions']
            self.publicKey = base64.b64decode(responseJson['publicKey'])

            box = Box(keys, PublicKey(self.publicKey))
            data = box.decrypt(cipherText, nonce=nonce)

            self.symmetricKey = data[0:PrivateKey.SIZE]
            self.symmetricNonce = data[PrivateKey.SIZE:]

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
                self._get_url('auth'),
                headers=headers
        )
        if r.status_code == 200:
            return True
        else:
            return False

    def mkdir(self, dirPath, isPrivate, isVersioned, isPathShared, metadata=None):
        headers = {
                'authorization': 'Bearer %s' % self.token,
                'Content-Type': 'text/plain'
        }
        payload = {
                'dirPath': dirPath,
                'isPrivate': isPrivate,
                'metadata': metadata,
                'isVersioned': isVersioned,
                'isPathShared': isPathShared
        }
        r = self._post_encrypted('nfs/directory', headers, payload)
        if r.status_code == 200:
            return True, 'Ok'
        else:
            return False, self._decrypt_response(r.text)

    def get_dir(self, dirPath, isPathShared=False):
        headers = {
                'Authorization': 'Bearer %s' % self.token
        }
        dirPath = urllib.quote_plus(dirPath)
        # requires lower case
        isPathShared = 'true' if isPathShared else 'false'
        url = self._get_url('nfs/directory/%s/%s' % (dirPath, isPathShared))
        r = response = requests.get(
                url,
                headers=headers
        )
        # TODO find other status codes and generate responses
        if r.status_code == 200 or r.status_code == 400:
            return self._decrypt_response(r.text)
        else:
            return None

    def post_file(self, filePath, isPrivate, isVersioned, isPathShared,
            metadata=None):
        headers = {
            'Authorization': 'Bearer %s' % self.token
        }
        payload = {
            'filePath': filePath,
            'isPRivate': isPrivate,
            'metadata': metadata,
            'isVersioned': isVersioned,
            'isPathShared': isPathShared
        }
        r = self._post_encrypted('nfs/file', headers, payload)
        if r.status_code == 200:
            return True
        else:
            return False, self._decrypt_response(r.text)

    def get_file(self, dirPath, isPathShared=False,
            offset=None, length=None):
        headers = {
                'Authorization': 'Bearer %s' % self.token
        }
        args = {}
        if offset is not None:
            args['offset'] = offset
        if length is not None:
            args['length'] = length
        dirPath = urllib.quote_plus(dirPath)
        # requires lower case
        isPathShared = 'true' if isPathShared else 'false'
        url = self._get_url('nfs/file/%s/%s' % (dirPath, isPathShared))
        if args:
            url = url + "?" + urllib.urlencode(args)
        r = response = requests.get(
                url,
                headers=headers
        )
        # TODO find other status codes and generate responses
        if r.status_code == 200 or r.status_code == 400:
            return self._decrypt_response(r.text, is_json=False)
        else:
            return None

    def put_file(self, data, filePath, isPathShared=False, offset=None):
        headers = {
            'Authorization': 'Bearer %s' % self.token
        }
        args = {}
        if offset is not None:
            args['offset'] = offset
        filePath = urllib.quote_plus(filePath)
        isPathShared = 'true' if isPathShared else 'false'
        url = 'nfs/file/%s/%s' % (filePath, isPathShared)
        if args:
            url = url + "?" + urllib.urlencode(args)
        r = self._put_encrypted(url, headers, data)
        if r.status_code == 200:
            return True
        else:
            return False, self._decrypt_response(r.text)

    def post_dns(self, longName, serviceName, serviceHomeDirPath, isPathShared=False):
        headers = {
            'Authorization': 'Bearer %s' % self.token
        }
        payload = {
            'longName': longName,
            'serviceName': serviceName,
            'serviceHomeDirPath': serviceHomeDirPath,
            'isPathShared': isPathShared
        }
        r = self._post_encrypted('dns', headers, payload)
        print r.status_code
        print r.text
        if r.status_code == 200:
            return True
        else:
            return False, self._decrypt_response(r.text)

if __name__=='__main__':
    s = Safe('Test', '0.0.1', 'hintofbasil', 'com.github.hintofbasil')
    if s.authenticate(permissions=['SAFE_DRIVE_ACCESS']):
        folder = '/www6'
        filename = '/index.html'
        data = '<html><body><h1>Test successful</h1></body></html>'
        print "1", s.is_authenticated()
        print "2", s.mkdir(folder, False, False, True)
        print "3", s.get_dir(folder, isPathShared=True)
        print "4", s.post_file(folder + filename, True, False, True)
        print "5", s.put_file('This is test data', folder + filename,
                isPathShared=True)
        print "6", s.get_file(folder + filename, True)
        print "7", s.post_dns('hintofbasil6', 'www', folder, isPathShared=True)
