#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.abspath('../safeAPI/'))
sys.path.insert(0, os.path.abspath('safeAPI/'))

from safeAPI import Safe

import unittest

class Authorization(unittest.TestCase):

    def setUp(self):
        self.safe = Safe('unittests2',
                '0.0.2',
                'hintofbasil2',
                'com.github.hintofbasil2'
                )
        self.safe.authenticate(permissions=[])

    def testIsAuthenticateSuccess(self):
        response = self.safe.is_authenticated()
        self.assertTrue(response is True)

    def testDeauthenticate(self):
        self.safe.deauthenticate()
        response = seld.safe.is_authenticated()
        self.assertTrue(response is false)

if __name__=='__main__':
    unittest.main()
