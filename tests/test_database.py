import pytest

import app.database as database

from app.middleware import db



@pytest.mark.usefixtures('c')
def test_all_office_tickets(c):
    """
    Test a method in class Database that retrieves all tickets for a given office.
    The method is all_office_tickets
    """

    # make two offices using class Office, give name and prefix alphabet
    office1 = database.Office(name="Office 1", prefix="A")
    office2 = database.Office(name="Office 2", prefix="B")
    db.session.add(office1)
    db.session.add(office2)
    db.session.commit()

    #now make a task using class Task, give name and hidden status
    task1 = database.Task(name="Task 1", hidden=False)
    db.session.add(task1)
    db.session.commit()

    #now make the task common task to both the offices

    office1.tasks.append(task1)
    office2.tasks.append(task1)
    db.session.commit()

    # now make some new tickets using create_new_ticket method in class Serial
    # parameters passed are task object, office object and name_or_number

    ticket1 = database.Serial.create_new_ticket(task=task1, office=office1, name_or_number="Ticket 1")[0]
    ticket2 = database.Serial.create_new_ticket(task=task1, office=office1, name_or_number="Ticket 2")[0]
    ticket3 = database.Serial.create_new_ticket(task=task1, office=office2, name_or_number="Ticket 3")[0]
    db.session.commit()
    # now test the all_office_tickets method for office1
    office1_tickets = database.Serial.all_office_tickets(office_id=office1.id).all()
    assert len(office1_tickets) == 2

    office1_tickets_ids = [ticket.id for ticket in office1_tickets]
    assert ticket1.id in office1_tickets_ids
    assert ticket2.id in office1_tickets_ids


    assert ticket3.id not in office1_tickets_ids
    
    # now test the all_office_tickets method for office2
    office2_tickets = database.Serial.all_office_tickets(office_id=office2.id).all()
    assert len(office2_tickets) == 1

    office2_tickets_ids = [ticket.id for ticket in office2_tickets]
    assert ticket3.id in office2_tickets_ids
    assert ticket1.id not in office2_tickets_ids
    assert ticket2.id not in office2_tickets_ids