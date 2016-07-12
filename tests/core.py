#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.abspath('../safeAPI/'))
sys.path.insert(0, os.path.abspath('safeAPI/'))

from safeAPI import Safe, SafeException

import random
import string
import unittest

class SafeCore(unittest.TestCase):

    def setUp(self):
        self.safe = Safe('unittests',
                '0.0.1',
                'hintofbasil',
                'com.github.hintofbasil'
                )
        self.safe.authenticate(permissions=[])

    def testIsAuthenticateSuccess(self):
        response = self.safe.is_authenticated()
        self.assertTrue(response is True)

    def testDeauthenticate(self):
        self.safe.deauthenticate()
        response = self.safe.is_authenticated()
        self.assertTrue(response is false)

    def testDirectoryCreate(self):
        path = ''.join(
                random.choice(string.ascii_lowercase) for _ in range(10)
            )
        # Valid create
        self.assertEqual(self.safe.mkdir('app', path, False), True)
        # Double create
        with self.assertRaises(SafeException) as cm:
            self.safe.mkdir('app', path, False)
        self.assertEqual(cm.exception.json()['errorCode'], -502)

if __name__=='__main__':
    unittest.main()
