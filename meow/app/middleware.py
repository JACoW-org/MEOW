from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
# from starlette.middleware.trustedhost import TrustedHostMiddleware

origins = [
    'http://127.0.0.1:8005',
    'https://indico.jacow.org',
    'https://indico.akera.net'
]

methods = ['*']
headers = ['*']

credentials = True

middleware: list[Middleware] = [
    # Middleware(HTTPSRedirectMiddleware),
    # Middleware(TrustedHostMiddleware,
    #            allowed_hosts=['*.jacow.org']),
    # Middleware(CORSMiddleware, allow_origins=['*'])
    Middleware(CORSMiddleware, allow_origins=origins,
               allow_methods=methods, allow_headers=headers,
               allow_credentials=credentials)
]
