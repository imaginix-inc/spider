from typing import Callable, Awaitable, List
from .schools import ucr, usf, ucsc
from .models import BaseDB, DeclarativeBase
from . import models


class Spider:
    def __init__(self, school_name: str, func: Callable[[], Awaitable[List[BaseDB]]], scheme: DeclarativeBase, school_id: int):
        self.school_name = school_name
        self.func = func
        self.scheme = scheme
        self.school_id = school_id


spiders: List[Spider] = [
    Spider(school_name='ucr', func=ucr.main,
           scheme=models.USCCourseDB, school_id=111),
    Spider(school_name='usf', func=usf.main,
           scheme=models.USFCourseDB, school_id=112),
]
