import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base


@pytest.fixture()
def client():
    # use in-memory sqlite for tests
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as c:
        yield c

    session.close()
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


# some reusable CSV content for tests
SAMPLE_CSV = """employee_id,employee_name,department,date,hours_worked
1,John Smith,Engineering,2026-06-01,8
1,John Smith,Engineering,2026-06-02,9
2,Mary Johnson,Finance,2026-06-01,7
3,Alice Wong,Engineering,2026-06-01,13
4,Bob Martinez,HR,2026-06-01,8
5,Carol Davis,Finance,2026-06-01,10
"""


def make_file(content=SAMPLE_CSV):
    return {"file": ("attendance.csv", io.BytesIO(content.encode()), "text/csv")}
