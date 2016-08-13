import requests
import base64
import json
import urllib
import sys
from os.path import expanduser

class SafeException(Exception):

    def __init__(self, response):
        self._raw_text = response.text
        s = '<[%d] %s>' % (response.status_code, response.text)
        super(SafeException, self).__init__(s)

    def json(self):
        return json.loads(self._raw_text)

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

    def _post_file(self, path, payload, content):
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': sys.getsizeof(content)
        }
        if self.token:
            headers['Authorization'] = 'Bearer %s' % self.token
        url = self._get_url(path)
        payload = json.dumps(payload)
        r = requests.post(url,
            data=content,
            headers=headers)
        return r

    def authenticate(self, permissions=[]): #TODO check is needs to = None
        if self._get_saved_token():
            return True
        payload = {
            'app': {
                'name': self.name,
                'version': self.version,
                'vendor': self.vendor,
                'id': self.id
            },
            'permissions': permissions
        }
        r = self._post('auth', payload)
        if r.status_code == 200:
            responseJson = r.json()
            self.token = responseJson['token']
            self.permissions = responseJson['permissions']
            self._save_token()
            return True
        else:
            return False

    def _get_saved_token(self):
        try:
            with open(expanduser('~/.safe_store'), 'r') as f:
                self.token = f.read()
            if self.is_authenticated():
                return True
            else:
                self.token = ''
                return False
        except:
            return None

    def _save_token(self):
        try:
            with open(expanduser('~/.safe_store'), 'w') as f:
                f.write(self.token)
        except:
            pass

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

    def mkdir(self, rootPath, dirPath, metadata=None):
        payload = {
            'metadata': metadata,
        }
        url = 'nfs/directory/%s/%s' % (rootPath, dirPath)
        r = self._post(url, payload)
        if r.status_code == 200:
            return True
        else:
            raise SafeException(r)

    def get_dir(self, rootPath, dirPath):
        url = 'nfs/directory/%s/%s' % (rootPath, dirPath)
        r = self._get(url)
        if r.status_code == 200:
            return json.loads(r.text)
        elif r.status_code == 401:
            raise SafeException(r)
        else:
            return None

    def create_file(self, rootPath, filePath, content, metadata=None):
        payload = {
            'metadata': metadata,
        }
        url = 'nfs/file/%s/%s' % (rootPath, filePath)
        if content:
            r = self._post_file(url, payload, content)
        else:
            r = self._post(url, payload)
        if r.status_code == 200:
            return True
        else:
            raise SafeException(r)

    def read_file(self, rootPath, dirPath):
        path = 'nfs/file/%s/%s' % (rootPath, dirPath)
        r = self._get(path)
        if r.status_code == 200:
            return r.text
        elif r.status_code == 401:
            raise SafeException(r)
        else:
            return None

    def register_dns(self, rootPath, longName, serviceName, serviceHomeDirPath):
        payload = {
            'rootPath': rootPath,
            'longName': longName,
            'serviceName': serviceName,
            'serviceHomeDirPath': serviceHomeDirPath,
        }
        r = self._post('dns', payload)
        if r.status_code == 200:
            return True
        else:
            raise SafeException(r)

    def get_dns(self, longName):
        url = 'dns/%s' % longName
        r = self._get(url)
        if r.status_code == 200:
            return json.loads(r.text)
        elif r.status_code == 401:
            raise SafeException("Unauthorised")
        else:
            return None
