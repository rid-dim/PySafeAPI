#!/usr/bin/env python

from safeAPI import Safe 

import sys

folder = '/www'
filename = '/index.html'
fileData = '<html><body><h1>Test successful</h1></body></html>'
dnsName = 'DNSNAME'

# Allow easy overriding of constants for testing
try:
    dnsName = sys.argv[1]
    fileData = sys.argv[2]
except IndexError:
    pass

if __name__=='__main__':
    # Create Safe opject
    s = Safe('Website Upload Test', '0.0.1', 'hintofbasil',
            'com.github.hintofbasil')
    # Authenticate against safe network
    if s.authenticate(permissions=['SAFE_DRIVE_ACCESS']):
        # Check if folder already exists
        if not s.get_dir('drive', folder):
            # If it doesn't exist create folder
            s.mkdir('drive', folder)
        #Check if file exists
        if not s.read_file('drive', folder + filename):
            # If file doesn't exist create file
            s.create_file('drive', folder + filename, fileData)
        # TODO get_dns
        # Create DNS entry
        s.register_dns('drive', dnsName, 'www', folder)
