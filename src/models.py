from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func, SmallInteger, BigInteger, Float
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


class USFCourseDB(BaseDB):
    __tablename__ = 'usf_courses'
    term = mapped_column(String(50))
    course_code = mapped_column(String(20))
    section = mapped_column(String(10))
    campus = mapped_column(String(100))
    schedule_type = mapped_column(String(50))
    instructional_method = mapped_column(String(50))
    credits = mapped_column(Float)
    capacity = mapped_column(Integer)
    actual = mapped_column(Integer)
    remaining = mapped_column(Integer)
    waitlist_capacity = mapped_column(Integer)
    waitlist_actual = mapped_column(Integer)
    waitlist_remaining = mapped_column(Integer)
    field_of_study = mapped_column(String(100))
    prerequisite_course = mapped_column(String(20))
    minimum_grade = mapped_column(String(2))

    def __repr__(self):
        # 自动获取所有字段及其值
        fields = {column.name: getattr(self, column.name)
                  for column in self.__table__.columns}
        return f"<User({fields})>"


class UCSCCourseDB(BaseDB):
    __tablename__ = 'ucsc_courses'
    subject = mapped_column(String)
    number = mapped_column(String)
    display_name = mapped_column(String)
    instruction_mode = mapped_column(String)
    academic_group = mapped_column(String)
    start_date = mapped_column(String)
    end_date = mapped_column(String)
    status = mapped_column(String)
    enrolled_count = mapped_column(Integer)
    max_enroll = mapped_column(Integer)
    waitlisted_count = mapped_column(Integer)
    max_waitlist = mapped_column(Integer)
    instructor_name = mapped_column(String)
    course_name = mapped_column(String)
    term = mapped_column(String)
    days = mapped_column(String)
    start_time = mapped_column(String)
    end_time = mapped_column(String)
    units = mapped_column(Integer)


