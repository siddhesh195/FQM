import pytest

import app.database as data

from app.middleware import db


# test to check if we can create a new ticket by passing task and office not linked

@pytest.mark.usefixtures("c")
def test_proper_new_ticket_generation():
    """
    test to check if we can create a new ticket by passing task and office not linked
    """

    # create a new office
    office = data.Office(name="Test Office")
    db.session.add(office)
    db.session.commit()

    #fetch the office
    office = data.Office.query.filter_by(name="Test Office").first()
    assert office is not None

    # create a new task
    task = data.Task(name="Test Task")
    db.session.add(task)
    db.session.commit()
    
    # fetch the task
    task = data.Serial.query.filter_by(name="Test Task").first()
    assert task is not None

    # create a new ticket using class helper method
    ticket, exception = data.Ticket.create_new_ticket(task=task, office=office,name_or_number="Test Ticket")

    assert ticket is not None

    
