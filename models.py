from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint
from app.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, nullable=False)
    employee_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    hours_worked = Column(Float, nullable=False)

    # prevent importing the same employee+date twice
    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="uq_emp_date"),
    )
