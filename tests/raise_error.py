import ujson

try:
    raise RuntimeError('Error')
except Exception as e:
    print(ujson.dumps(dict(error=e.args)))
