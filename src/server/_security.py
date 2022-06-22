from flask import request
from ._config import META_SECRET
from ._exceptions import UnAuthenticatedException

def check_meta_key():
    if request.values:
        meta_key = request.values.get("meta_key", None)
        if not (meta_key and meta_key == META_SECRET):
            raise UnAuthenticatedException()
