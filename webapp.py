import meow.app.factory as factory
import logging as lg
import os

os.environ['CLIENT_TYPE'] = 'webapp'

# lg.basicConfig(level=lg.INFO)

lg.basicConfig(
    level=lg.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = factory.build()
