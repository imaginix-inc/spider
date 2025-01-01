from typing import Callable, Awaitable, List
from .schools import ucr, usf, uci, ucsd
from .models import BaseDB, DeclarativeBase
from . import models


class Spider:
    def __init__(self, school_name: str, func: Callable[[], Awaitable[List[BaseDB]]], scheme: DeclarativeBase, school_id: int):
        self.school_name = school_name
        self.func = func
        self.scheme = scheme
        self.school_id = school_id


spiders: List[Spider] = [
    # Spider(school_name='ucr', func=ucr.main,
    #        scheme=models.UCRCourseDB, school_id=1076),
    # Spider(school_name='usf', func=usf.main,
    #        scheme=models.USFCourseDB, school_id=1600),
    # Spider(school_name='uci', func=uci.main,
    #        scheme=models.UCICourseDB, school_id=13221),
    Spider(school_name='ucsd', func=ucsd.main,
           scheme=models.UCSDCourseDB, school_id=1079),
]
