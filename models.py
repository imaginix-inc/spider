from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func, SmallInteger, BigInteger
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import DeferredReflection


class BaseDB(DeclarativeBase):
    __abstract__ = True
    id = mapped_column(BigInteger, primary_key=True)
    source_url = mapped_column(String)
    remark = mapped_column(String)
    creator = mapped_column(String, default='')
    create_time = mapped_column(DateTime, nullable=False, default=func.now())
    updater = mapped_column(String, default='')
    update_time = mapped_column(DateTime, nullable=False, default=func.now())
    deleted = mapped_column(SmallInteger, nullable=False, default=0)
    tenant_id = mapped_column(BigInteger, nullable=False, default=0)
    name_vector = mapped_column(Vector)
    search_vector = mapped_column(TSVECTOR)


class USCCourseDB(BaseDB):
    __abstract__ = False
    __tablename__ = 'usc_courses'
    section = mapped_column(String)
    units = mapped_column(String)
    offering_title = mapped_column(String)
    instructor = mapped_column(String)
    days = mapped_column(String)
    time = mapped_column(String)
    location = mapped_column(String)
    grade_scheme = mapped_column(String)
    registered = mapped_column(String)
    total_seats = mapped_column(String)
    from schools.ucr.extract import Course

    @ classmethod
    def from_pydantic(cls, course: Course):
        return cls(
            section=course.section,
            units=course.units,
            offering_title=course.offering_title,
            instructor=course.instructor,
            days=course.days,
            time=course.time,
            location=course.location,
            grade_scheme=course.grade_scheme,
            registered=course.registered,
            total_seats=course.total_seats
        )
