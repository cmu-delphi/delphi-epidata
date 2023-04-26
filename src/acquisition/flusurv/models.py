from sqlalchemy import Column, Index, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import Date, Float, Integer, String

Base = declarative_base()


class FluSurv(Base):
    """
    SQLAlchemy model representing flusurve data.
    """

    __tablename__ = 'flusurv'
    __table_args__ = (
        UniqueConstraint("issue", "epiweek", "location", name="issue"),
        Index("release_date", "release_date"),
        Index("issue_2", "issue"),
        Index("epiweek", "epiweek"),
        Index("region", "location"),
        Index("lag", "lag"),
    )

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False)
    release_date = Column(Date, nullable=False)
    issue = Column(Integer, nullable=False)
    epiweek = Column(Integer, nullable=False)
    location = Column(String(length=32), nullable=False)
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
