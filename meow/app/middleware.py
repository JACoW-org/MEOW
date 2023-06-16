from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
# from starlette.middleware.trustedhost import TrustedHostMiddleware

middleware: list[Middleware] = [
    # Middleware(HTTPSRedirectMiddleware),
    # Middleware(TrustedHostMiddleware,
    #            allowed_hosts=['*.jacow.org']),
    # Middleware(CORSMiddleware, allow_origins=['*'])
    Middleware(CORSMiddleware, allow_origins=['https://indico.jacow.org', 'https://indico.akera.net'], allow_methods=['*'],
               allow_headers=['*'], allow_credentials=True)
]

