# JPSP-NG - INSTALL

## SETUP

```
cd jpsp-ng
python3 -m venv venv

. ./venv/bin/activate
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements-dev.txt
```


## RUN

```
./venv/bin/python main.py
./venv/bin/pytest ./tests
```
