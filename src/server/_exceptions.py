from typing import Iterable, Optional
from flask import make_response, request
from flask.json import dumps
from werkzeug.exceptions import HTTPException

from delphi_utils import get_structured_logger


def _is_using_status_codes() -> bool:
    # classic and tree are old school
    return request.values.get("format", "classic") not in ["classic", "tree"]


class EpiDataException(HTTPException):
    def __init__(self, message: str, status_code: int = 500):
        super(EpiDataException, self).__init__(message)
        self.code = status_code if _is_using_status_codes() else 200
        self.response = make_response(
            dumps(dict(result=-1, message=message, epidata=[])),
            self.code,
        )
        self.response.mimetype = "application/json"


class MissingOrWrongSourceException(EpiDataException):
    def __init__(self, endpoints: Iterable[str]):
        super(MissingOrWrongSourceException, self).__init__(f"no data source specified, possible values: {','.join(endpoints)}", 400)


class ValidationFailedException(EpiDataException):
    def __init__(self, message: str):
        super(ValidationFailedException, self).__init__(message, 400)


class DatabaseErrorException(EpiDataException):
    def __init__(self, details: Optional[str] = None):
        if details:
            # Internal details are logged server-side only; the client-facing
            # message stays generic so SQL text, driver messages, and hostnames
            # are never disclosed to clients (see #1801).
            get_structured_logger("server_error").error("database error", details=details)
        super(DatabaseErrorException, self).__init__("database error", 500)
