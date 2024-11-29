from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
# from starlette.middleware.trustedhost import TrustedHostMiddleware

origins = [    
    'https://indico.jacow.org',
    'https://indico.akera.net',
    'http://indico:8000',
    'http://localhost:8000',
    'http://localhost:8005',
]

methods = ['*']
headers = ['*']

credentials = True

middleware: list[Middleware] = [
    # Middleware(HTTPSRedirectMiddleware),
    # Middleware(TrustedHostMiddleware,
    #            allowed_hosts=['*.jacow.org']),
    # Middleware(CORSMiddleware, allow_origins=['*'])
    Middleware(GZipMiddleware, 
               minimum_size=512, 
               compresslevel=1),
    Middleware(CORSMiddleware, 
               allow_origins=origins,
               allow_methods=methods, 
               allow_headers=headers,
               allow_credentials=credentials)
]
