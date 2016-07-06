from nacl.public import PrivateKey, Box, PublicKey
from nacl.bindings.crypto_box import (crypto_box_afternm,
        crypto_box_open_afternm)
import nacl.utils
import requests
import base64
import json
import urllib

class SafeException(Exception):
    pass

class Safe:

    def __init__(self,
            name,
            version,
            vendor,
            id,
            addr='http://localhost',
            port=8100,
            isShared=False):
        self.name = name
        self.version = version
        self.vendor = vendor
        self.id = id
        self.url = "%s:%d/" % (addr, port)
        self.isShared = isShared
        self.token = ""

    def _get_url(self, location):
        return self.url + location

    def _get(self, path):
        headers = {
            'Content-Type': 'application/json'
        }
        if self.token:
            headers['Authorization'] = 'Bearer %s' % self.token
        url = self._get_url(path)
        r = requests.get(url,
            headers=headers)
        return r

    def _post(self, path, payload):
        headers = {
            'Content-Type': 'application/json'
        }
        if self.token:
            headers['Authorization'] = 'Bearer %s' % self.token
        url = self._get_url(path)
        payload = json.dumps(payload)
        r = requests.post(url,
            data=payload,
            headers=headers)
        return r

    def _post_encrypted(self, path, payload):
        if not self.symmetricNonce or not self.symmetricKey:
            raise SafeException("Unauthorised")
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer %s' % self.token
        }
        url = self._get_url(path)
        payload = json.dumps(payload)
        encryptedData = crypto_box_afternm(payload, self.symmetricNonce,
                self.symmetricKey)
        payload = base64.b64encode(encryptedData)
        r = requests.post(url,
            data=payload,
            headers=headers)
        return r

    def _put_encrypted(self, path, payload, isJson=False):
        if not self.symmetricNonce or not self.symmetricKey:
            raise SafeException("Unauthorised")
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer %s' % self.token
        }
        url = self._get_url(path)
        if isJson:
            payload = json.dumps(payload)
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
        r = self._post('auth', payload)
        if r.status_code == 200:
            responseJson = r.json()
            self.token = responseJson['token']
            self.permissions = responseJson['permissions']
            return True
        else:
            return False

    def is_authenticated(self):
        try: # If not token saved definitely not authenticated
            self.token
        except AttributeError:
            return False

        r = self._get('auth')
        if r.status_code == 200:
            return True
        else:
            return False

    def mkdir(self, dirPath, isPrivate, isVersioned, isPathShared=None, metadata=None):
        if isPathShared is None:
            isPathShared = self.isShared

        payload = {
                'dirPath': dirPath,
                'isPrivate': isPrivate,
                'metadata': metadata,
                'isVersioned': isVersioned,
                'isPathShared': isPathShared
        }
        r = self._post_encrypted('nfs/directory', payload)
        if r.status_code == 200:
            return True
        else:
            raise SafeException(self._decrypt_response(r.text))

    def get_dir(self, dirPath, isPathShared=None):
        if isPathShared is None:
            isPathShared = self.isShared

        isPathShared = self.isShared or isPathShared
        dirPath = urllib.quote_plus(dirPath)
        # requires lower case
        isPathShared = 'true' if isPathShared else 'false'
        path = 'nfs/directory/%s/%s' % (dirPath, isPathShared)
        r = self._get(path)
        if r.status_code == 200:
            return self._decrypt_response(r.text)
        elif r.status_code == 401:
            raise SafeException("Unauthorised")
        else:
            return None

    def post_file(self, filePath, isPrivate, isVersioned,
            isPathShared=None, metadata=None):
        if isPathShared is None:
            isPathShared = self.isShared

        payload = {
            'filePath': filePath,
            'isPRivate': isPrivate,
            'metadata': metadata,
            'isVersioned': isVersioned,
            'isPathShared': isPathShared
        }
        r = self._post_encrypted('nfs/file', payload)
        if r.status_code == 200:
            return True
        else:
            raise SafeException(self._decrypt_response(r.text))

    def get_file(self, dirPath, isPathShared=None,
            offset=None, length=None):
        if isPathShared is None:
            isPathShared = self.isShared

        args = {}
        if offset is not None:
            args['offset'] = offset
        if length is not None:
            args['length'] = length
        dirPath = urllib.quote_plus(dirPath)
        # requires lower case
        isPathShared = 'true' if isPathShared else 'false'
        path = 'nfs/file/%s/%s' % (dirPath, isPathShared)
        if args:
            path = path + "?" + urllib.urlencode(args)
        r = self._get(path)
        if r.status_code == 200:
            return self._decrypt_response(r.text, is_json=False)
        elif r.status_code == 401:
            raise SafeException("Unauthorised")
        else:
            return None

    def put_file(self, data, filePath, isPathShared=None, offset=None):
        if isPathShared is None:
            isPathShared = self.isShared

        args = {}
        if offset is not None:
            args['offset'] = offset
        filePath = urllib.quote_plus(filePath)
        isPathShared = 'true' if isPathShared else 'false'
        path = 'nfs/file/%s/%s' % (filePath, isPathShared)
        if args:
            path = path + "?" + urllib.urlencode(args)
        r = self._put_encrypted(path, data)
        if r.status_code == 200:
            return True
        else:
            raise SafeException(self._decrypt_response(r.text))

    def post_dns(self, longName, serviceName, serviceHomeDirPath,
            isPathShared=None):
        if isPathShared is None:
            isPathShared = self.isShared

        payload = {
            'longName': longName,
            'serviceName': serviceName,
            'serviceHomeDirPath': serviceHomeDirPath,
            'isPathShared': isPathShared
        }
        r = self._post_encrypted('dns', payload)
        if r.status_code == 200:
            return True
        else:
            raise SafeException(self._decrypt_response(r.text))

    def get_dns(self, longName):
        longName = urllib.quote_plus(longName)
        path = 'dns/%s' % longName
        r = self._get(path)
        if r.status_code == 200:
            return self._decrypt_response(r.text)
        elif r.status_code == 401:
            raise SafeException("Unauthorised")
        else:
            return None

    def put_dns(self, longName, serviceName, serviceHomeDirPath,
            isPathShared=None):
        if isPathShared is None:
            isPathShared = self.isShared

        payload = {
            'longName': longName,
            'serviceName': serviceName,
            'serviceHomeDirPath': serviceHomeDirPath,
            'isPathShared': isPathShared
        }
        r = self._put_encrypted('dns', payload, isJson=True)
        if r.status_code == 200:
            return True
        else:
            raise SafeException(self._decrypt_response(r.text))
