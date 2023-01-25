# JPSP-NG - INSTALL

### https://realpython.com/intro-to-pyenv/
curl https://pyenv.run | bash


## SETUP

```
cd jpsp-ng
python3 -m venv venv

. ./venv/bin/activate
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements-dev.txt
```


pip list --outdated 


## RUN

```
./venv/bin/python main.py
./venv/bin/pytest ./tests
```


htop -u fabio.meneghetti -F "python main"

