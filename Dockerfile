# https://github.com/tiangolo/uvicorn-gunicorn-docker/tree/master/docker-images

FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./jinja /code/app/jinja
COPY ./meow /code/app/meow
COPY ./ssl /code/app/ssl
COPY ./static /code/app/static
COPY ./webui /code/app/webui

COPY ./asgi.py /code/app/asgi.py
COPY ./main.py /code/app/main.py

WORKDIR /code/app

CMD ["python", "main.py"]

# CMD ["uvicorn", "asgi:app", "--host", "0.0.0.0", \
#      "--port", "8080","--workers", "4","--loop", "uvloop", \
#      "--http", "httptools","--ws", "wsproto", "--log-level", "warning"]
