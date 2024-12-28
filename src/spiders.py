from typing import Callable, Awaitable, List
from .schools import ucr, usf, ucsc
from .models import BaseDB, DeclarativeBase
from . import models


class Spider:
    def __init__(self, school_name: str, func: Callable[[], Awaitable[List[BaseDB]]], scheme: DeclarativeBase):
        self.school_name = school_name
        self.func = func
        self.scheme = scheme


spiders: List[Spider] = [
    Spider(school_name='ucr', func=ucr.main, scheme=models.USCCourseDB),
    Spider(school_name='usf', func=usf.main, scheme=models.USFCourseDB),
    Spider(school_name='ucsc', func=ucsc.main, scheme=models)
]
