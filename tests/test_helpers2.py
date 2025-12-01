import pytest
from app import helpers2
from app.middleware import db

class FakeSerial:
    def __init__(self,id,name,pulled_by, office,task,status):
        self.id = id
        self.name = name
        self.pulledBy = pulled_by
        self.pdt = None
        self.office = office
        self.task = task
        self.status = status

    
class FakeOffice:
    def __init__(self,id,name,timestamp):
        self.id = id
        self.name = name
        self.timestamp = timestamp
       

    @property
    def display_text(self):
        return self.name


class FakeTask:
    def __init__(self,id,name):
        self.id = id 
        self.name = name


class Query:
    def __init__(self,data):
        self.data =data
        self.filters= {}
    def filter_by(self,**kwargs):
        self.filters.update(kwargs)
        return self
    def first(self):
        for key,value in self.filters.items():
            for obj in self.data:
                if getattr(obj,key) == value:
                    return obj
        return None


class FakeUser:
    db= []
    def __init__(self,id,name):
        self.id = id
        self.name = name

class FakeCurrentUser:
    def __init__(self, authenticated):
        self.authenticated = authenticated
        self.last_seen = None
        
    @classmethod
    def is_authenticated(self):
        return self.authenticated
    
        

class Fake_Session:
    def __init__(self):
        self.added=None
        self.committed=None

    def add(self,data):
            self.added=data
    def commit(self):
        self.committed= self.added
    

class FakeDB:
    db_data=None

    @property
    def session(cls):
        return Fake_Session()


@pytest.mark.usefixtures('c')
def test_process_all_pulled_tickets(monkeypatch):

    monkeypatch.setattr(helpers2,'User', FakeUser)
    office1 = FakeOffice(1,'Office1',None)
    task1 = FakeTask(1,'Task1')
   
    user1=FakeUser(1,'User1')
    user2=FakeUser(2,'User2')

    FakeUser.db= [user1,user2]

    FakeUser.query = Query(FakeUser.db)

    from app.helpers2 import process_all_pulled_tickets

    
    tickets = [
        FakeSerial(1,'Ticket1',1,office1,task1,"Waiting"),
        FakeSerial(2,'Ticket2',2,office1,task1,"Waiting"),
    ]
    result = process_all_pulled_tickets(tickets)
    assert len(result) == 2
    assert result[0]['name'] == 'Ticket1'
    assert result[0]['pulled_by'] == 'User1'
    assert result[0]['office'] == 'Office1'
    assert result[0]['task'] == 'Task1'


@pytest.mark.usefixtures('c')
def test_last_pulled_ticket_by_each_user(monkeypatch):

    monkeypatch.setattr(helpers2,'User', FakeUser)
    office1 = FakeOffice(1,'Office1',None)
    task1 = FakeTask(1,'Task1')
   
    user1=FakeUser(1,'User1')
    user2=FakeUser(2,'User2')

    FakeUser.db= [user1,user2]

    FakeUser.query = Query(FakeUser.db)

    from app.helpers2 import last_pulled_ticket_by_each_user

    
    tickets = [
        FakeSerial(1,'Ticket1',1,office1,task1,"Waiting"),
        FakeSerial(2,'Ticket2',1,office1,task1,"Waiting"),
        FakeSerial(3,'Ticket3',2,office1,task1,"Waiting"),
    ]
    tickets[0].pdt = 10
    tickets[1].pdt = 20
    tickets[2].pdt = 15

    result = last_pulled_ticket_by_each_user(tickets)
    assert len(result) == 2
    assert result[1]['name'] == 'Ticket2'  # Last ticket for user 1
    assert result[2]['name'] == 'Ticket3'  # Only ticket for user 2

@pytest.mark.usefixtures('c')
def test_generate_token_for_task():
    from app.helpers2 import generate_token_for_task
    token = generate_token_for_task()
    assert len(token) == 8
    assert token.isupper()

@pytest.mark.usefixtures('c')
def test_get_translation(monkeypatch):
    from app.helpers2 import get_translation

    class FakeTranslator:
        def translate(self, text, dest):
            class Result:
                def __init__(self, text):
                    self.text = text + "_translated"
            return Result(text).text

    monkeypatch.setattr(helpers2, 'gtranslator', FakeTranslator())

    translated = get_translation("Hello", "es")
    assert translated == "Hello_translated"

@pytest.mark.usefixtures('c')
def test_update_last_seen_helper(monkeypatch):
    from app.helpers2 import update_last_seen_helper

    FakeCurrentUserInstance = FakeCurrentUser(authenticated=True)
    db= FakeDB()
    monkeypatch.setattr(helpers2,'current_user', FakeCurrentUserInstance)
    monkeypatch.setattr(helpers2,'db', db)

    update_last_seen_helper()


@pytest.mark.usefixtures('c')
def test_build_reports_excel():
    from app.helpers2 import build_reports_excel
    import os
    import pandas as pd
    mock_data = {
    "Office A": {
        "total_count": 15,
        "attended_count": 10,
        "unattended_count": 5,
        "waiting_count": 3,
        "processed_count": 7,
    },
    "Office B": {
        "total_count": 20,
        "attended_count": 12,
        "unattended_count": 8,
        "waiting_count": 1,
        "processed_count": 11,
    }
}


    excel_io, filename = build_reports_excel(mock_data)

    # Save locally to test
    
    with open(filename, "wb") as f:
        f.write(excel_io.read())
    
    
    df = pd.read_excel(filename)
    
    try:
        assert df['Office'][0]=="Office A"
        assert df['Office'][1]=="Office B"
        assert df['Total'][0]==15
        assert df['Total'][1]== 20
        assert df['Processing'][0]==10
        assert df['Processing'][1]== 12
        assert df['Pulled'][0]==5
        assert df['Pulled'][1]== 8
        assert df['Unpulled'][0]==3
        assert df['Unpulled'][1]== 1
        assert df['Processed'][0]==7
        assert df['Processed'][1]== 11
        
    
    finally:
        os.remove(filename)
    
@pytest.mark.usefixtures('c')
def test_fetch_tickets_by_date_range(monkeypatch):
    from app.helpers2 import fetch_tickets_by_date_range
    from app.database import Serial, Task, Office
    import datetime as dt

    timestamps_of_tokens ={
        "Token 1":{"year":2022,"month":1,"day":1,"hour":10,"minute":0,"second":0},
        "Token 2":{"year":2022,"month":1,"day":4,"hour":10,"minute":0,"second":0},
        "Token 3":{"year":2022,"month":2,"day":7,"hour":10,"minute":0,"second":0},
        "Token 4":{"year":2022,"month":3,"day":11,"hour":10,"minute":0,"second":0},
        "Token 5":{"year":2022,"month":7,"day":1,"hour":10,"minute":0,"second":0},
        "Token 6":{"year":2022,"month":8,"day":1,"hour":10,"minute":0,"second":0},
        "Token 7":{"year":2022,"month":9,"day":14,"hour":10,"minute":0,"second":0},
        "Token 8":{"year":2022,"month":10,"day":16,"hour":10,"minute":0,"second":0}
    }

    def initialize_data():

        def create_tickets():

            Serial.create_new_ticket(task=task1, office=office1, name_or_number="Token 1")
            Serial.create_new_ticket(task=task2, office=office1, name_or_number="Token 2")
            Serial.create_new_ticket(task=task2, office=office1, name_or_number="Token 3")
            Serial.create_new_ticket(task=task2, office=office1, name_or_number="Token 4")
            
            Serial.create_new_ticket(task=task1, office=office1, name_or_number="Token 5")
            Serial.create_new_ticket(task=task3, office=office1, name_or_number="Token 6")
            Serial.create_new_ticket(task=task3, office=office1, name_or_number="Token 7")
            Serial.create_new_ticket(task=task3, office=office1, name_or_number="Token 8")
            
            
            db.session.commit()
            

        Office1 = Office(name='Office1')
        

        Task1 = Task(name='Task1')
        Task2 = Task(name='Task2')
        Task3 = Task(name='Task3')

        db.session.add(Office1)
       
        db.session.add(Task1)
        db.session.add(Task2)
        db.session.add(Task3)
        db.session.commit()
        task1 = Task.query.filter_by(name='Task1').first()
        task2 = Task.query.filter_by(name='Task2').first()
        task3 = Task.query.filter_by(name='Task3').first()

        office1 = Office.query.filter_by(name='Office1').first()
      
        create_tickets()
    
    def replace_timestamps(tickets,year=2023,month=1,day=1,time_hour=0,time_minute=0,time_second=0):
        
        for ticket in tickets:
            ticket.timestamp = ticket.timestamp.replace(year=year, month=month, day=day, hour=time_hour, minute=time_minute, second=time_second,microsecond=0)
        db.session.commit()
    
    initialize_data()
    all_offices_query_object = Office.query
    office1 = all_offices_query_object.filter_by(name='Office1').first()

    get_all_office_tickets = Serial.all_office_tickets(office_id=office1.id)

    

    for ticket in get_all_office_tickets:
        timestamp_info = timestamps_of_tokens.get(ticket.name)
        replace_timestamps([ticket], year=timestamp_info['year'], month=timestamp_info['month'], day=timestamp_info['day'], time_hour=timestamp_info['hour'], time_minute=timestamp_info['minute'], time_second=timestamp_info['second'])

    start_date1 = dt.datetime(2022, 1, 1, 0, 0, 0)
    end_date1 = dt.datetime(2022, 6, 30, 23, 59, 59)

    start_date2 = dt.datetime(2022, 7, 1, 0, 0, 0)
    end_date2 = dt.datetime(2022, 12, 31, 23, 59, 59)

    get_all_office_tickets = fetch_tickets_by_date_range(start_date1, end_date1)['Office1']

    get_all_office_tickets2 = fetch_tickets_by_date_range(start_date2, end_date2)['Office1']

    assert get_all_office_tickets == {'Task1': 1, 'Task2': 3}
    assert get_all_office_tickets2 == {'Task1': 1, 'Task3': 3}
