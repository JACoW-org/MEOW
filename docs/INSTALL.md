# MEOW - INSTALL

### https://realpython.com/intro-to-pyenv/
curl https://pyenv.run | bash


## SETUP

```
cd meow
python3 -m venv venv

. ./venv/bin/activate
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/pip install -r requirements.txt
```


pip list --outdated 


rm -rfv venv ; python3 -m venv venv ; . ./venv/bin/activate ; ./venv/bin/pip install --upgrade pip ; ./venv/bin/pip install -r requirements-dev.txt

## RUN

```
./venv/bin/python main.py
./venv/bin/pytest ./tests
```


htop -u fabio.meneghetti -F "venv/bin/python3 worker"


rm -rfv venv ; python3 -m venv venv ; . ./venv/bin/activate ; ./venv/bin/pip install --upgrade pip

./venv/bin/pip install starlette uvicorn websockets uvloop anyio redis minify_html odfpy lxml orjson nltk ulid pymupdf pymupdf-fonts pikepdf rdflib jinja2 aiohttp unidecode pytz supervisor

./venv/bin/pip install pylance autopep8 flake8      
