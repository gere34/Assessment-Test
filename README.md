# Assessment-Test
# Attendance Analytics API

A simple REST API that imports employee attendance CSV files and provides analytics endpoints.

Built with FastAPI + SQLite. Should take about 2 minutes to get running.

---

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API will be at http://localhost:8000
Swagger docs at http://localhost:8000/docs

---

## Database

Using SQLite (attendance.db gets created automatically on first run).

Schema:

```sql
CREATE TABLE attendance (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id  INTEGER NOT NULL,
    employee_name TEXT NOT NULL,
    department   TEXT NOT NULL,
    date         DATE NOT NULL,
    hours_worked REAL NOT NULL,
    UNIQUE(employee_id, date)
);
```

The unique constraint on employee_id + date means you can safely re-import the same CSV without getting duplicates — skipped rows are reported back in the response.

---

## Endpoints

### POST /attendance/import
Upload a CSV file to import records.

```bash
curl -X POST http://localhost:8000/attendance/import \
  -F "file=@sample_attendance.csv"
```

Response:
```json
{
  "message": "done",
  "rows_imported": 18,
  "rows_skipped": 0,
  "errors": []
}
```

CSV must have these columns: `employee_id, employee_name, department, date, hours_worked`

---

### GET /employees/{id}/hours
Total hours worked by an employee.

```bash
curl http://localhost:8000/employees/1/hours
```

```json
{
  "employee_id": 1,
  "employee_name": "John Smith",
  "department": "Engineering",
  "total_hours": 30.0
}
```

Returns 404 if employee not found.

---

### GET /departments/analytics
Average daily hours per department.

```json
{
  "departments": [
    {
      "department": "Engineering",
      "avg_hours_per_day": 10.5,
      "num_employees": 3
    }
  ]
}
```

---

### GET /employees/top
Top 5 employees by total hours worked.

```json
{
  "top_employees": [
    {
      "rank": 1,
      "employee_id": 3,
      "employee_name": "Alice Wong",
      "total_hours": 33.0
    }
  ]
}
```

---

### GET /employees/anomalies
Flags any day where someone worked more than 12 hours.

```json
{
  "anomalies": [
    {
      "employee_id": 3,
      "employee_name": "Alice Wong",
      "department": "Engineering",
      "date": "2026-06-02",
      "hours_worked": 14.0
    }
  ],
  "total": 1
}
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Notes

- If you want to use PostgreSQL instead of SQLite, just change `DATABASE_URL` in `app/database.py`
- The anomaly threshold is set to 12 hours in `app/service.py` (ANOMALY_THRESHOLD constant)
- Re-importing the same CSV is safe — duplicates get skipped and counted
