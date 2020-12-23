from typing import List, Optional
from fastapi import Query

def parse_str_list_generator(
    default: Optional[List[str]] = None, title=None, description=None
):
    def parse_str_list(
        param: str = Query(default=default, title=title, description=description)
    ) -> Optional[List[str]]:
        return param.split(",") if param else None

    return parse_str_list


def parse_int_list_generator(
    default: Optional[List[int]] = None, title=None, description=None
):
    def parse_int_list(
        param: str = Query(default=default, title=title, description=description)
    ) -> Optional[List[int]]:
        return [int(v) for v in param.split(",")] if param else None

    return parse_int_list