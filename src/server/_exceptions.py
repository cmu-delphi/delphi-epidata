from flask import make_response, request
from flask.json import dumps
from typing import Iterable
from werkzeug.exceptions import HTTPException


def _is_using_status_codes() -> bool:
    # classic and tree are old school
    return request.values.get("format", "classic") not in ["classic", "tree"]


class EpiDataException(HTTPException):
    def __init__(self, message: str, status_code: int = 500, analytics=True):
        super(EpiDataException, self).__init__(message)
        self.code = status_code if _is_using_status_codes() else 200
        self.response = make_response(
            dumps(dict(result=-1, message=message)),
            self.code,
        )
        self.response.mimetype = "application/json"
        if analytics:
            # lazy to avoid circular references
            from ._analytics import record_analytics

            record_analytics(-1)


class MissingOrWrongSourceException(EpiDataException):
    def __init__(self, endpoints: Iterable[str]):
        super(MissingOrWrongSourceException, self).__init__(
            f"no data source specified, possible values: {','.join(endpoints)}", 400
        )


class UnAuthenticatedException(EpiDataException):
    def __init__(self):
        super(UnAuthenticatedException, self).__init__("unauthenticated", 401)


class ValidationFailedException(EpiDataException):
    def __init__(self, message: str):
        super(ValidationFailedException, self).__init__(message, 400)


class DatabaseErrorException(EpiDataException):
    def __init__(self):
        super(DatabaseErrorException, self).__init__("database error", 500, False)
