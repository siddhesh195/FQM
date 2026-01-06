import pytest
from app.middleware import db
import app.database as data

from app.constants import TICKET_ATTENDED, TICKET_WAITING, TICKET_PROCESSED


def _make_serial(db_session, office, task, number, name, printed=False, status=None,p=False):
    # This mirrors your real creation logic
    s = data.Serial(
        number=number,
        office_id=office.id,
        task_id=task.id,
        name=name,
        n=not printed,
        p=p
    )
    if status is not None:
        s.status = status   # field used by your Query properties
    db_session.session.add(s)
    return s

@pytest.mark.usefixtures("c")
def test_reports_home(c):
    resp = c.get("/reports")   # adjust prefix
    assert resp.status_code == 200
    assert b"Reports Dashboard" in resp.data
    assert b"Task Frequency Report" in resp.data
    assert b"Ticket Status Report" in resp.data
    assert b"Select a Report to View" in resp.data

@pytest.mark.usefixtures("c")
def test_reports_data(c):
    office = data.Office(name="Pune Office")
    task = data.Task(name="Dummy Task")
    db.session.add_all([office, task])
    db.session.commit()

    t1 = _make_serial(
        db,
        office=office,
        task=task,
        number=1,
        name="T1",
        printed=False,
        p=True,
        status=TICKET_ATTENDED,
    )

    t2 = _make_serial(
        db,
        office=office,
        task=task,
        number=2,
        name="T2",
        printed=False,
        status=TICKET_WAITING,
    )

    t3 = _make_serial(
        db,
        office=office,
        task=task,
        number=3,
        name="T3",
        printed=True,
        p=True,
        status=TICKET_PROCESSED,
    )

   
    db.session.commit()

    resp = c.get("/reports_data")   # adjust prefix
    assert resp.status_code == 200
    
    data_json = resp.get_json()

    
    stats = data_json["statistics_by_office_name"]["Pune Office"]


    assert stats["total_count"] == 3
    assert stats["attended_count"] == 1
    assert stats["waiting_count"] == 1
    assert stats["processed_count"] == 1

@pytest.mark.usefixtures("c")
def test_make_reports_excel(c):
    office = data.Office(name="Pune Office")
    task = data.Task(name="Dummy Task")
    db.session.add_all([office, task])
    db.session.commit()

    t1 = _make_serial(
        db,
        office=office,
        task=task,
        number=1,
        name="T1",
        printed=False,
        p=True,
        status=TICKET_ATTENDED,
    )

    t2 = _make_serial(
        db,
        office=office,
        task=task,
        number=2,
        name="T2",
        printed=False,
        status=TICKET_WAITING,
    )

    t3 = _make_serial(
        db,
        office=office,
        task=task,
        number=3,
        name="T3",
        printed=True,
        p=True,
        status=TICKET_PROCESSED,
    )

   
    db.session.commit()

    resp = c.get("/make_reports_excel")   # adjust prefix
    assert resp.status_code == 200
    assert resp.headers["Content-Disposition"].startswith("attachment;")
    assert "spreadsheetml" in resp.headers["Content-Type"]


@pytest.mark.usefixtures("c")
def test_make_task_reports_success(c):
    from app.database import Serial, Office

    all_offices = Office.query.all()
    

    payload = {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }

    resp = c.post("/make_task_frequency_reports", json=payload)   # adjust prefix
    assert resp.status_code == 200
    response_json = resp.get_json()
    
    first_office_name = all_offices[0].name
    assert first_office_name in response_json.keys()
    assert isinstance(response_json[first_office_name], dict)


@pytest.mark.usefixtures("c")
def test_make_task_reports_invalid_date(c):
    payload = {
        "start_date": "invalid-date",
        "end_date": "2024-12-31"
    }

    resp = c.post("/make_task_frequency_reports", json=payload)   # adjust prefix
   
    response_json = resp.get_json()
    assert "error" in response_json
    assert response_json["error"] == "Invalid date format. Use YYYY-MM-DD."


@pytest.mark.usefixtures("c")
def test_make_task_reports_start_date_after_end_date(c):
    payload = {
        "start_date": "2024-12-31",
        "end_date": "2024-01-01"
    }

    resp = c.post("/make_task_frequency_reports", json=payload)   # adjust prefix
   
    response_json = resp.get_json()
    assert "error" in response_json
    assert response_json["error"] == "Start date cannot be after end date."


@pytest.mark.usefixtures("c")
def test_make_task_reports_helper_function_error(c,monkeypatch):
    from app.views import reports
    def broken_fetch_tickets_by_date_range(start_date, end_date):
        raise Exception("Simulated error")
    
    monkeypatch.setattr(reports, "fetch_tickets_by_date_range", broken_fetch_tickets_by_date_range)

    payload = {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    resp = c.post("/make_task_frequency_reports", json=payload)   # adjust prefix
    response_json = resp.get_json()
    assert "error" in response_json
    assert response_json["error"] == "some error occurred"