PySafeAPI
=========

A python wrapper around the [Safe Launcher API](https://maidsafe.readme.io/docs/introduction).

Installation
------------

PySafeAPI is installable from PyPi using the following command:

`pip install SafeAPI`

This will not include the examples which are downloadable by cloning this repository.

Progress
--------
#### Authorization
- [x] POST /auth
- [x] GET /auth
- [ ] DELTE /auth

#### NFS Directory
- [x] POST /nfs/directory/:rootPath/:directoryPath
- [x] GET /nfs/directory/:rootPath/:directoryPath/
- [x] PUT /nfs/directory/:rootPath/:directoryPath
- [x] POST /nfs/movedir
- [x] DELETE /nfs/directory/:rootPath/:directoryPath

#### NFS File
- [x] POST /nfs/file/:rootPath/:filePath
- [ ] HEAD /nfs/file/:rootPath/:filePath
- [x] GET /nfs/file/:rootPath/:filePath
- [ ] PUT /nfs/file/metadata/:rootPath/:filePath
- [ ] POST /nfs/movefile
- [x] DELETE /nfs/file/:rootPath/:filePath

#### DNS
- [x] POST /dns/:longName
- [x] POST /dns
- [x] PUT /dns
- [x] GET /dns
- [x] GET /dns/:longName
- [x] GET /dns/:serviceName/:longName
- [ ] GET /dns/:serviceName/:longName/:filePath
- [x] DELETE /dns/:serviceName/:longName
- [x] DELETE /dns/:longName

Examples
--------

A selection of examples are located in the examples folder.  They can be run using the following command 

`python -m examples.EXAMPLE_NAME`

E.g To run the upload webpage example run

`python -m examples.upload_webpage`

Contributions
-------------

If you would like to contribute to the development of this project please feel free to submit a pull request.

Pull requests should be submitted to the current development branch.  Pull requests to master may be rejected.

Contributions for any of the missing URLs, extra examples, documentation and bug fixes are all welcome.
