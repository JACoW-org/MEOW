import meow.app.factory as factory
import logging as lg
import os

os.environ['CLIENT_TYPE'] = 'webapp'

lg.basicConfig(level=lg.INFO)

app = factory.build()
