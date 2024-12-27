from typing import Callable, Awaitable, List
from .schools import ucr
from .models import BaseDB, DeclarativeBase
from . import models


class Spider:
    def __init__(self, school_name: str, func: Callable[[], Awaitable[List[BaseDB]]], scheme: DeclarativeBase):
        self.school_name = school_name
        self.func = func
        self.scheme = scheme


spiders: List[Spider] = [
    Spider(school_name='ucr', func=ucr.main, scheme=models.USCCourseDB),
]
