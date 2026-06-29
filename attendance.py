

ORM model for attendance records.

Table: attendance_records
- id             : surrogate primary key (auto-increment)
- employee_id    : business key from source data
- employee_name  : name at time of import (denormalised for simplicity)
- department     : department at time of import
- date           : calendar date of the work day
- hours_worked   : decimal hours; supports fractional hours (e.g. 7.5)

A UNIQUE constraint on (employee_id, date) prevents duplicate imports for
the same employee on the same day and enables idempotent re-imports.
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, UniqueConstraint
from app.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id   = Column(Integer, nullable=False, index=True)
    employee_name = Column(String(120), nullable=False)
    department    = Column(String(120), nullable=False, index=True)
    date          = Column(Date, nullable=False)
    hours_worked  = Column(Numeric(5, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="uq_employee_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<AttendanceRecord employee_id={self.employee_id} "
            f"date={self.date} hours={self.hours_worked}>"
        )
