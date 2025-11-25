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