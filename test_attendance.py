import io
import pytest
from tests.conftest import SAMPLE_CSV, make_file


class TestImport:

    def test_basic_import_works(self, client):
        resp = client.post("/attendance/import", files=make_file())
        assert resp.status_code == 200
        data = resp.json()
        assert data["rows_imported"] == 6

    def test_wrong_file_type_rejected(self, client):
        f = {"file": ("data.txt", io.BytesIO(b"not a csv"), "text/plain")}
        resp = client.post("/attendance/import", files=f)
        assert resp.status_code == 400

    def test_duplicate_rows_skipped(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.post("/attendance/import", files=make_file())
        data = resp.json()
        assert data["rows_skipped"] == 6
        assert data["rows_imported"] == 0

    def test_missing_column_returns_error(self, client):
        bad = "employee_id,employee_name\n1,John\n"
        f = {"file": ("bad.csv", io.BytesIO(bad.encode()), "text/csv")}
        resp = client.post("/attendance/import", files=f)
        assert resp.status_code == 422

    def test_bad_hours_row_is_skipped_not_fatal(self, client):
        csv = (
            "employee_id,employee_name,department,date,hours_worked\n"
            "1,John,Engineering,2026-06-01,8\n"
            "2,Mary,Finance,2026-06-01,999\n"  # invalid hours
            "3,Bob,HR,2026-06-01,7\n"
        )
        resp = client.post("/attendance/import", files=make_file(csv))
        data = resp.json()
        assert data["rows_imported"] == 2
        assert len(data["errors"]) == 1


class TestEmployeeHours:

    def test_get_hours_for_existing_employee(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/employees/1/hours")
        assert resp.status_code == 200
        data = resp.json()
        assert data["employee_id"] == 1
        assert data["total_hours"] == 17.0  # 8 + 9

    def test_unknown_employee_gives_404(self, client):
        resp = client.get("/employees/999/hours")
        assert resp.status_code == 404

    def test_response_has_name_and_dept(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/employees/1/hours")
        data = resp.json()
        assert "employee_name" in data
        assert "department" in data


class TestDeptAnalytics:

    def test_returns_all_departments(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/departments/analytics")
        assert resp.status_code == 200
        depts = [d["department"] for d in resp.json()["departments"]]
        assert "Engineering" in depts
        assert "Finance" in depts
        assert "HR" in depts

    def test_avg_hours_is_correct(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/departments/analytics")
        depts = {d["department"]: d for d in resp.json()["departments"]}
        # HR has only Bob: 8hrs, so avg should be 8
        assert depts["HR"]["avg_hours_per_day"] == 8.0

    def test_empty_db_returns_empty_list(self, client):
        resp = client.get("/departments/analytics")
        assert resp.json()["departments"] == []


class TestTopEmployees:

    def test_returns_5_by_default(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/employees/top")
        assert resp.status_code == 200
        assert len(resp.json()["top_employees"]) == 5

    def test_ordered_by_hours_desc(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/employees/top")
        hours = [e["total_hours"] for e in resp.json()["top_employees"]]
        assert hours == sorted(hours, reverse=True)

    def test_rank_starts_at_1(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/employees/top")
        assert resp.json()["top_employees"][0]["rank"] == 1

    def test_empty_db(self, client):
        resp = client.get("/employees/top")
        assert resp.json()["top_employees"] == []


class TestAnomalies:

    def test_detects_over_12_hours(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/employees/anomalies")
        assert resp.status_code == 200
        # Alice worked 13hrs so should show up
        emp_ids = [a["employee_id"] for a in resp.json()["anomalies"]]
        assert 3 in emp_ids

    def test_no_anomalies_when_all_normal(self, client):
        csv = (
            "employee_id,employee_name,department,date,hours_worked\n"
            "1,John,Engineering,2026-06-01,8\n"
            "2,Mary,Finance,2026-06-01,7\n"
        )
        client.post("/attendance/import", files=make_file(csv))
        resp = client.get("/employees/anomalies")
        assert resp.json()["total"] == 0

    def test_total_count_is_correct(self, client):
        client.post("/attendance/import", files=make_file())
        resp = client.get("/employees/anomalies")
        data = resp.json()
        assert data["total"] == len(data["anomalies"])
