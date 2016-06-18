#!/usr/bin/env python

from safeAPI import Safe 

folder = '/www'
filename = '/index.html'
fileData = '<html><body><h1>Test successful</h1></body></html>'
dns_name = 'hob3'

if __name__=='__main__':
    # Create Safe opject
    s = Safe('Website Upload Test', '0.0.1', 'hintofbasil',
            'com.github.hintofbasil', isShared=True)
    # Authenticate against safe network
    if s.authenticate(permissions=['SAFE_DRIVE_ACCESS']):
        # Check if folder already exists
        valid, _ = s.get_dir(folder)
        # If it doesn't exist create folder
        if not valid:
            s.mkdir(folder, False, False)
        # Check if file exists
        valid, _ = s.get_file(folder + filename, True)
        # If file doesn't exist create file
        if not valid:
            s.post_file(folder + filename, True, False, True)
        # Put data in file - overwrites current content
        s.put_file(fileData, folder + filename)
        # TODO get_dns
        # Create DNS entry
        s.post_dns(dns_name, 'www', folder)
