import pytest
from app import helpers2

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
        assert df['Attended'][0]==10
        assert df['Attended'][1]== 12
        assert df['Unattended'][0]==5
        assert df['Unattended'][1]== 8
        assert df['Waiting'][0]==3
        assert df['Waiting'][1]== 1
        assert df['Processed'][0]==7
        assert df['Processed'][1]== 11
        
    
    finally:
        os.remove(filename)
    






                    