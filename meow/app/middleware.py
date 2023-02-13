from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middleware: list[Middleware] = [
    # Middleware(HTTPSRedirectMiddleware),
    # Middleware(TrustedHostMiddleware,
    #            allowed_hosts=['meow.local', '*.meow.local']),
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'],
               allow_headers=['*'], allow_credentials=True)
]
