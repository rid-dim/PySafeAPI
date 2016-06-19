PySafeAPI
=========

A python wrapper around the [Safe Launcher API](https://maidsafe.readme.io/docs/introduction).

Installation
------------

PySafeAPI is not currently on PyPi due to it's infancy.  Installation currently requires copying safeAPI.py to your project's location.
`mv safeAPI.py YOUR_LOCATION`

Progress
--------

- [x] POST /auth
- [x] GET /auth
- [ ] DELETE /auth
- [x] POST /nfs/directory
- [x] GET /nfs/directory/:dirPath/:isPathShared
- [ ] DELETE /nfs/directory/:dirPath/:isPathShared
- [x] POST /nfs/file
- [x] GET /nfs/file/:filePath/:isPathShared
- [x] PUT /nfs/file/:filePath/:isPathShared
- [ ] DELETE /nfs/file/:dirPath/:isPathShared
- [ ] POST /dns/:longName
- [x] POST /dns
- [ ] PUT /dns
- [ ] GET /dns
- [x] GET/dns/:longName
- [ ] GET /dns/:serviceName/:longName
- [ ] GET /dns/:serviceName/:longName/

Examples
--------

A selection of examples are located in the examples folder.  They can be run using the following command 
`python -m examples.EXAMPLE_NAME`
E.g To run the upload webpage example run
`python -m examples.upload_webpage`

Contributions
-------------

If you would like to contribute to the development of this project please feel free to submit a pull request.  Contributions for any of the missing URLs, extra examples, documentation and bug fixes are all welcome.

