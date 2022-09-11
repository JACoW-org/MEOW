from starlette.middleware import Middleware

middleware: list[Middleware] = [
    # Middleware(HTTPSRedirectMiddleware),
    # Middleware(TrustedHostMiddleware,
    #            allowed_hosts=['jpsp.local', '*.jpsp.local']),
    # Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'],
    #            allow_headers=['*'], allow_credentials=True)
]
