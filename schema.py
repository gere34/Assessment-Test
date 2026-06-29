from pydantic import BaseModel
from datetime import date


class ImportResponse(BaseModel):
    message: str
    rows_imported: int
    rows_skipped: int
    errors: list[str] = []


class EmployeeHours(BaseModel):
    employee_id: int
    employee_name: str
    department: str
    total_hours: float

    class Config:
        from_attributes = True


# used for top employees list too
class TopEmployee(BaseModel):
    rank: int
    employee_id: int
    employee_name: str
    total_hours: float


class DeptSummary(BaseModel):
    department: str
    avg_hours_per_day: float
    num_employees: int


class AnomalyRecord(BaseModel):
    employee_id: int
    employee_name: str
    department: str
    date: date
    hours_worked: float
