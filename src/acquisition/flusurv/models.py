from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Date, Float, Integer, String

Base = declarative_base()


class FluSurv(Base):
    """
    SQLAlchemy model representing flusurve data.
    """

    __tablename__ = 'flusurv'

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False)
    release_date = Column(Date, nullable=False)
    issue = Column(Integer, unique=True, nullable=False)
    epiweek = Column(Integer, unique=True, nullable=False)
    location = Column(String(length=32), unique=True, nullable=False)
    lag = Column(Integer, nullable=False)
    rate_age_0 = Column(Float, default=None)
    rate_age_1 = Column(Float, default=None)
    rate_age_2 = Column(Float, default=None)
    rate_age_3 = Column(Float, default=None)
    rate_age_4 = Column(Float, default=None)
    rate_age_5 = Column(Float, default=None)
    rate_age_6 = Column(Float, default=None)
    rate_age_7 = Column(Float, default=None)
    rate_overall = Column(Float, default=None)
