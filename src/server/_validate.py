from flask import Request

from ._exceptions import ValidationFailedException


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
