import pytest
from app.middleware import db
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





                    