# Secrets Management Utility
A wrapper utility for interacting with aws secrets manager. Does not contain any credentials or secrets.

# Build
```
poetry version <new version>
poetry build
poetry publish
```

# Test install
```
docker run --rm -it python:3 bash
pip install secmgr
python -m secmgr -k testkey
```

# Load local dir into python docker container
```
docker run --rm -it -v `pwd`:/var/secmgr -w /var/secmgr python:3 bash
pip install poetry

```
