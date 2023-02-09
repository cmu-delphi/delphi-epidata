from typing import Optional

from flask import Request

from ._exceptions import UnAuthenticatedException, ValidationFailedException


def resolve_auth_token(request: Request) -> Optional[str]:
    # auth request param
    if "auth" in request.values:
        return request.values["auth"]
    # user name password
    if request.authorization and request.authorization.username == "epidata":
        return request.authorization.password
    # bearer token authentication
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :]
    return None


def check_auth_token(request: Request, token: str, optional=False) -> bool:
    value = resolve_auth_token(request)

    if value is None:
        if optional:
            return False
        else:
            raise ValidationFailedException(f"missing parameter: auth")

    valid_token = value == token
    if not valid_token and not optional:
        raise UnAuthenticatedException()
    return valid_token


def require_all(request: Request, *values: str) -> bool:
    """
    returns true if all fields are present in the request otherwise raises an exception
    :returns bool
    """
    for value in values:
        if not request.values.get(value):
            raise ValidationFailedException(f"missing parameter: need [{', '.join(values)}]")
    return True


def require_any(request: Request, *values: str, empty=False) -> bool:
    """
    returns true if any fields are present in the request otherwise raises an exception
    :returns bool
    """
    for value in values:
        if request.values.get(value) or (empty and value in request.values):
            return True
    raise ValidationFailedException(f"missing parameter: need one of [{', '.join(values)}]")
