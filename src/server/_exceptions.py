from typing import Iterable, Optional
from flask import make_response, request
from flask.json import dumps
from werkzeug.exceptions import HTTPException

from ._config import RETIREMENT_MESSAGE, RETIREMENT_RESULT_CODE


def _is_using_status_codes() -> bool:
    # classic and tree are old school
    return request.values.get("format", "classic") not in ["classic", "tree"]


class EpiDataException(HTTPException):
    def __init__(self, message: str, status_code: int = 500, result_code: int = -1):
        super(EpiDataException, self).__init__(message)
        self.code = status_code if _is_using_status_codes() else 200
        self.response = make_response(
            dumps(dict(result=result_code, message=message, epidata=[])),
            self.code,
        )
        self.response.mimetype = "application/json"


class MissingOrWrongSourceException(EpiDataException):
    def __init__(self, endpoints: Iterable[str]):
        super(MissingOrWrongSourceException, self).__init__(f"no data source specified, possible values: {','.join(endpoints)}", 400)


class ValidationFailedException(EpiDataException):
    def __init__(self, message: str):
        super(ValidationFailedException, self).__init__(message, 400)


class DataRetiredException(EpiDataException):
    """
    raised when a request asks only for time values this API no longer serves.

    uses HTTP 410 Gone and its own `result` code so clients can tell it apart from an ordinary
    validation error (-1) or a legitimately empty result set (-2).
    """

    def __init__(self, details: Optional[str] = None):
        msg = RETIREMENT_MESSAGE
        if details:
            msg = f"{msg} ({details})"
        super(DataRetiredException, self).__init__(msg, 410, result_code=RETIREMENT_RESULT_CODE)


class DatabaseErrorException(EpiDataException):
    def __init__(self, details: Optional[str] = None):
        msg = "database error"
        if details:
            msg = f"{msg}: {details}"
        super(DatabaseErrorException, self).__init__(msg, 500)
