from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app import models
from app import service
from app.schemas import ImportResponse, EmployeeHours, TopEmployee, DeptSummary, AnomalyRecord

# create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Attendance Analytics API")


@app.post("/attendance/import", response_model=ImportResponse)
def import_attendance(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        result = service.import_csv(file.file, db)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return result


@app.get("/employees/{employee_id}/hours", response_model=EmployeeHours)
def employee_hours(employee_id: int, db: Session = Depends(get_db)):
    result = service.get_employee_hours(employee_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result


@app.get("/departments/analytics")
def dept_analytics(db: Session = Depends(get_db)):
    data = service.get_dept_analytics(db)
    return {"departments": data}


@app.get("/employees/top")
def top_employees(db: Session = Depends(get_db)):
    data = service.get_top_employees(db)
    return {"top_employees": data}


@app.get("/employees/anomalies")
def anomalies(db: Session = Depends(get_db)):
    data = service.get_anomalies(db)
    return {"anomalies": data, "total": len(data)}
