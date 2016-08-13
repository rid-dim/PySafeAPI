#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.abspath('../safeAPI/'))
sys.path.insert(0, os.path.abspath('safeAPI/'))

from safeAPI import Safe, SafeException

import random
import string
import unittest

ROOT_DIR = 'app'

class SafeCore(unittest.TestCase):

    def setUp(self):
        self.safe = Safe('unittests',
                '0.0.1',
                'hintofbasil',
                'com.github.hintofbasil'
                )
        if ROOT_DIR == 'app':
            self.safe.authenticate(permissions=[])
        elif ROOT_DIR == 'drive':
            self.safe.authenticate(permissions=['SAFE_DRIVE_ACCESS'])

    def generate_path(self, depth=1):
        add = lambda x,y: x + y
        paths = [''.join(
                    random.choice(string.ascii_lowercase) for _ in range(10)
                ) + '/'
                for _ in range(depth)]
        return reduce(add, paths)[:-1]

    def testIsAuthenticateSuccess(self):
        response = self.safe.is_authenticated()
        self.assertTrue(response is True)

    def testDeauthenticate(self):
        self.safe.deauthenticate()
        response = self.safe.is_authenticated()
        self.assertTrue(response is false)

    def testDirectoryCreate(self):
        path = self.generate_path()
        # Valid create
        self.assertEqual(self.safe.mkdir(ROOT_DIR, path), True)
        # Double create
        with self.assertRaises(SafeException) as cm:
            self.safe.mkdir(ROOT_DIR, path)
        self.assertEqual(cm.exception.json()['errorCode'], -502)

    def testDirectoryGet(self):
        path = self.generate_path()
        # Get non existant directory
        self.assertEqual(self.safe.get_dir(ROOT_DIR, path), None)
        # Must create before getting
        self.safe.mkdir(ROOT_DIR, path)
        response = self.safe.get_dir(ROOT_DIR, path)
        self.assertTrue(response is not None)
        self.assertEqual(response['info']['name'], path)

    def testDirectoryPut(self):
        path = self.generate_path()
        newPath = self.generate_path()
        self.safe.mkdir(ROOT_DIR, path)
        response = self.safe.update_dir(ROOT_DIR, path, newPath)
        self.assertTrue(response)
        response = self.safe.get_dir(ROOT_DIR, newPath)
        self.assertTrue(response is not None)
        self.assertEqual(response['info']['name'], newPath)

    def testDirectoryMove(self):
        path = self.generate_path()
        newPath = self.generate_path()
        self.safe.mkdir(ROOT_DIR, path)
        # Destination path must exist
        self.safe.mkdir(ROOT_DIR, newPath)
        response = self.safe.move_dir(ROOT_DIR, path,
                ROOT_DIR, newPath)
        self.assertTrue(response)
        response = self.safe.get_dir(ROOT_DIR, newPath)
        self.assertTrue(response is not None)
        self.assertEqual(response['info']['name'], newPath)

    def testDirectoryDelete(self):
        path = self.generate_path()
        self.safe.mkdir(ROOT_DIR, path)
        response = self.safe.get_dir(ROOT_DIR, path)
        self.assertTrue(response is not None)
        self.assertEqual(response['info']['name'], path)
        response = self.safe.delete_dir(ROOT_DIR, path)
        self.assertTrue(response)
        response = self.safe.get_dir(ROOT_DIR, path)
        self.assertEqual(response, None)


    def testFileCreate(self):
        path = self.generate_path()
        response = self.safe.create_file(ROOT_DIR, path, None)
        self.assertEqual(response, True)

    def testFileCreateWithContent(self):
        path = self.generate_path()
        response = self.safe.create_file(ROOT_DIR, path, "Test data")
        self.assertEqual(response, True)

    def testFileRead(self):
        content = "Test data"
        path = self.generate_path()
        self.safe.create_file(ROOT_DIR, path, content)
        response = self.safe.read_file(ROOT_DIR, path)
        self.assertEqual(response, content)

    def testFileCreateMissingDirectory(self):
        path = self.generate_path(depth=2)
        with self.assertRaises(SafeException) as cm:
            self.safe.create_file(ROOT_DIR, path, None)
        self.assertEqual(cm.exception.json()['errorCode'], -1502)

    def testDnsRegister(self):
        longname = self.generate_path()
        serviceName = self.generate_path()
        path = self.generate_path()
        self.safe.mkdir(ROOT_DIR, path)
        response = self.safe.register_dns(ROOT_DIR, longname, serviceName, path)
        self.assertTrue(response, True)

    def testDnsGetLongNames(self):
        longname1 = self.generate_path()
        longname2 = self.generate_path()
        self.safe.create_long_name(longname1)
        self.safe.create_long_name(longname2)
        response = self.safe.get_long_names()
        self.assertTrue(longname1 in response)
        self.assertTrue(longname2 in response)

    def testDnsGet(self):
        longname = self.generate_path()
        serviceName = self.generate_path()
        path = self.generate_path()
        self.safe.mkdir(ROOT_DIR, path)
        self.safe.register_dns(ROOT_DIR, longname, serviceName, path)
        response = self.safe.get_dns(longname)
        self.assertEqual(response, [serviceName])

    def testDnsCreateLongName(self):
        longname = self.generate_path()
        response = self.safe.create_long_name(longname)
        self.assertTrue(response)

    def testDnsGetNonExistant(self):
        longname = self.generate_path()
        response = self.safe.get_dns(longname)
        self.assertEqual(response, None)

    def testDnsGetServiceHomeDirectory(self):
        serviceName = self.generate_path()
        longName = self.generate_path()
        path = self.generate_path()
        self.safe.mkdir(ROOT_DIR, path)
        self.safe.register_dns(ROOT_DIR, longName, serviceName, path)
        response = self.safe.get_service_home_directory(serviceName, longName)
        self.assertTrue(response['info']['name'] == path)

    def testDeleteLongName(self):
        longName = self.generate_path()
        self.safe.create_long_name(longName)
        response = self.safe.get_long_names()
        self.assertTrue(longName in response)
        response = self.safe.get_long_names()
        self.assertTrue(response)
        response = self.safe.delete_long_name(longName)
        self.assertTrue(response)
        response = self.safe.get_long_names()
        self.assertTrue(longName not in response)

if __name__=='__main__':
    unittest.main()
