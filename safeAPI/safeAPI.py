
# coding: utf-8

# # safeAPI
# 
# This API is meant to be a not too bad documented gate to SafeNet while enabling fast and easy adaption to network changes

# Connection settings:
# 
# Apps can make HTTP requests to http://localhost:8100. This is a local REST server that is automatically started when the user opens SAFE Launcher.
# [Introduction to the Safe Launcher](https://tutorials.safedev.org/)

# In[ ]:

import requests
import json
import urllib
import hashlib
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


# ### the init function contains and maintains all essential information about the program
# 
# Info needed for authentication with the launcher:
# 
# ![info needed for authentication](authentication_body.png "body of authentication request in js")
# 
# 
# ### next we define the _get_url-function to simplify the other functions:

# In[ ]:

def _get_url(self, location):
    return self.url + location

Safe._get_url = _get_url


# ### for requests we need to include the issued token in the header of our request
# 
# Description of [Get immutable Data](https://api.safedev.org/low-level-api/immutable-data/read-immutable-data.html) is found at the Linked website
# 
# ![immutable_data](immutable_data_request_00.png "request format")
# ![immutable_data](immutable_data_request_01.png "request header")
# ![immutable_data](immutable_data_request_02.png "response format")

# In[ ]:

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

Safe._get = _get


# In[ ]:

def _post(self, path, payload):
    return self._request('POST', path, payload)

Safe._post = _post


# In[ ]:

def _request(self, request, path, payload):
    headers = {
        'Content-Type': 'application/json'
    }
    if self.token:
        headers['Authorization'] = 'Bearer %s' % self.token
    url = self._get_url(path)
    payload = json.dumps(payload)
    r = requests.request(request,
        url,
        data=payload,
        headers=headers)
    return r

Safe._request = _request


# In[ ]:

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

Safe._post_file = _post_file


# In[ ]:

def authenticate(self, permissions=[]): #TODO check is needs to = None
    # map is required as /auth returns unicode
    self.permissions = map(unicode, permissions)
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
    
Safe.authenticate = authenticate


# In[ ]:

def _get_saved_token(self):
    try:
        with open(expanduser('~/.safe_store'), 'r') as f:
            appHash = self._get_app_hash()
            tokens = json.loads(f.read())
            self.token = tokens[appHash]
        if self.is_authenticated():
            return True
        else:
            self.token = ''
            return False
    except (IOError, ValueError, KeyError):
        self.token = ''
        return False

Safe._get_saved_token = _get_saved_token


# In[ ]:

def _save_token(self):
    try:
        with open(expanduser('~/.safe_store'), 'r+') as f:
            appHash = self._get_app_hash()
            try:
                tokens = json.loads(f.read())
            except ValueError:
                tokens = {}
            tokens[appHash] = self.token
            f.seek(0)
            f.write(json.dumps(tokens))
            f.truncate()
    except IOError:
        pass

Safe._save_token = _save_token


# In[ ]:

def _get_app_hash(self):
    # Tokens will be in plain text - md5 will suffice
    m = hashlib.md5()
    m.update(self.name)
    m.update(self.version)
    m.update(self.vendor)
    m.update(self.id)
    m.update(str(self.permissions))
    return m.hexdigest()

Safe._get_app_hash = _get_app_hash


# In[ ]:

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

Safe.is_authenticated = is_authenticated


# In[ ]:

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

Safe.mkdir = mkdir


# In[ ]:

def get_dir(self, rootPath, dirPath):
    url = 'nfs/directory/%s/%s' % (rootPath, dirPath)
    r = self._get(url)
    if r.status_code == 200:
        return json.loads(r.text)
    elif r.status_code == 401:
        raise SafeException(r)
    else:
        return None

Safe.get_dir = get_dir


# In[ ]:

def update_dir(self, rootPath, dirPath, newPath, metadata=None):
    payload = {
        'name': newPath,
        'metadata': metadata
    }
    url = 'nfs/directory/%s/%s' % (rootPath, dirPath)
    r = self._request('put', url, payload)
    if r.status_code == 200:
        return True
    else:
        raise SafeException(r)

Safe.update_dir = update_dir


# In[ ]:

def move_dir(self, srcRootPath, srcPath,
        destRootPath, destPath, action='move'):
    payload = {
        'srcRootPath': srcRootPath,
        'srcPath': srcPath,
        'destRootPath': destRootPath,
        'destPath': destPath,
        'action': action
    }
    url = 'nfs/movedir'
    r = self._post(url, payload)
    if r.status_code == 200:
        return True
    else:
        raise SafeException(r)

Safe.move_dir = move_dir


# In[ ]:

def delete_dir(self, rootPath, dirPath):
    url = 'nfs/directory/%s/%s' % (rootPath, dirPath)
    r = self._request('delete', url, None)
    if r.status_code == 200:
        return True
    else:
        raise SafeException(r)

Safe.delete_dir = delete_dir


# In[ ]:

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

Safe.create_file = create_file


# In[ ]:

def read_file(self, rootPath, dirPath):
    path = 'nfs/file/%s/%s' % (rootPath, dirPath)
    r = self._get(path)
    if r.status_code == 200:
        return r.text
    elif r.status_code == 401:
        raise SafeException(r)
    else:
        return None

Safe.read_file = read_file


# In[ ]:

def delete_file(self, rootPath, filePath):
    path = 'nfs/file/%s/%s' % (rootPath, filePath)
    r = self._request('DELETE', path, None)
    if r.status_code == 200:
        return True
    else:
        raise SafeException(r)

Safe.delete_file = delete_file


# In[ ]:

def create_long_name(self, longname):
    url = 'dns/%s/' % longname
    r = self._post(url, None)
    if r.status_code == 200:
        return True
    else:
        raise SafeException(r)

Safe.create_long_name = create_long_name


# In[ ]:

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

Safe.register_dns = register_dns


# In[ ]:

def add_service(self, longName, serviceName, rootPath, serviceHomeDirPath):
    payload = {
        'longName': longName,
        'serviceName': serviceName,
        'rootPath': rootPath,
        'serviceHomeDirPath': serviceHomeDirPath
    }
    r = self._request('PUT', 'dns', payload)
    if r.status_code == 200:
        return True
    else:
        raise SafeException(r)
        
Safe.add_service = add_service


# In[ ]:

def get_long_names(self):
    url = 'dns/'
    r = self._get(url)
    if r.status_code == 200:
        return r.json()
    else:
        raise SafeException(r)

Safe.get_long_names = get_long_names


# In[ ]:

def get_dns(self, longName):
    url = 'dns/%s' % longName
    r = self._get(url)
    if r.status_code == 200:
        return json.loads(r.text)
    elif r.status_code == 401:
        raise SafeException("Unauthorised")
    else:
        return None

Safe.get_dns = get_dns


# In[ ]:

def get_service_home_directory(self, serviceName, longName):
    url = 'dns/%s/%s' % (serviceName, longName)
    r = self._get(url)
    if r.status_code == 200:
        return r.json()
    else:
        raise SafeException(r)

Safe.get_service_home_directory = get_service_home_directory


# In[ ]:

def delete_service_from_long_name(self, serviceName, longName):
    url = 'dns/%s/%s' % (serviceName, longName)
    r = self._request('DELETE', url, None)
    if r.status_code == 200:
        return True
    else:
        raise SafeException(r)

Safe.delete_service_from_long_name = delete_service_from_long_name


# In[ ]:

def delete_long_name(self, longName):
    url = 'dns/%s' % longName
    r = self._request('DELETE', url, None)
    if r.status_code == 200:
        return True
    else:
        raise SafeException(r)

Safe.delete_long_name = delete_long_name

