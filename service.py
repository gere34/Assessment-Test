import io
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.models import AttendanceRecord
from app.schemas import ImportResponse, EmployeeHours, TopEmployee, DeptSummary, AnomalyRecord

ANOMALY_THRESHOLD = 12.0


def import_csv(file, db: Session) -> ImportResponse:
    try:
        contents = file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise ValueError(f"Could not read CSV: {e}")

    # strip whitespace from column names just in case
    df.columns = df.columns.str.strip()

    required = {"employee_id", "employee_name", "department", "date", "hours_worked"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"CSV missing columns: {missing}")

    imported = 0
    skipped = 0
    errors = []

    for i, row in df.iterrows():
        try:
            hours = float(row["hours_worked"])
            if hours < 0 or hours > 24:
                errors.append(f"Row {i+2}: hours_worked out of range ({hours})")
                continue

            record = AttendanceRecord(
                employee_id=int(row["employee_id"]),
                employee_name=str(row["employee_name"]).strip(),
                department=str(row["department"]).strip(),
                date=pd.to_datetime(str(row["date"])).date(),
                hours_worked=hours,
            )
            db.add(record)
            db.flush()
            imported += 1

        except IntegrityError:
            db.rollback()
            skipped += 1
        except Exception as e:
            db.rollback()
            errors.append(f"Row {i+2}: {str(e)}")

    db.commit()

    return ImportResponse(
        message="done",
        rows_imported=imported,
        rows_skipped=skipped,
        errors=errors,
    )


def get_employee_hours(employee_id: int, db: Session):
    result = (
        db.query(
            AttendanceRecord.employee_id,
            AttendanceRecord.employee_name,
            AttendanceRecord.department,
            func.sum(AttendanceRecord.hours_worked).label("total_hours"),
        )
        .filter(AttendanceRecord.employee_id == employee_id)
        .group_by(AttendanceRecord.employee_id)
        .first()
    )

    if not result:
        return None

    return EmployeeHours(
        employee_id=result.employee_id,
        employee_name=result.employee_name,
        department=result.department,
        total_hours=round(result.total_hours, 2),
    )


def get_dept_analytics(db: Session) -> list[DeptSummary]:
    rows = (
        db.query(
            AttendanceRecord.department,
            func.avg(AttendanceRecord.hours_worked).label("avg_hours"),
            func.count(func.distinct(AttendanceRecord.employee_id)).label("emp_count"),
        )
        .group_by(AttendanceRecord.department)
        .all()
    )

    result = []
    for r in rows:
        result.append(DeptSummary(
            department=r.department,
            avg_hours_per_day=round(r.avg_hours, 2),
            num_employees=r.emp_count,
        ))
    return result


def get_top_employees(db: Session, limit=5) -> list[TopEmployee]:
    rows = (
        db.query(
            AttendanceRecord.employee_id,
            AttendanceRecord.employee_name,
            func.sum(AttendanceRecord.hours_worked).label("total"),
        )
        .group_by(AttendanceRecord.employee_id, AttendanceRecord.employee_name)
        .order_by(func.sum(AttendanceRecord.hours_worked).desc())
        .limit(limit)
        .all()
    )

    top = []
    for idx, r in enumerate(rows):
        top.append(TopEmployee(
            rank=idx + 1,
            employee_id=r.employee_id,
            employee_name=r.employee_name,
            total_hours=round(r.total, 2),
        ))
    return top


def get_anomalies(db: Session) -> list[AnomalyRecord]:
    rows = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.hours_worked > ANOMALY_THRESHOLD)
        .order_by(AttendanceRecord.hours_worked.desc())
        .all()
    )

    return [
        AnomalyRecord(
            employee_id=r.employee_id,
            employee_name=r.employee_name,
            department=r.department,
            date=r.date,
            hours_worked=r.hours_worked,
        )
        for r in rows
    ]
