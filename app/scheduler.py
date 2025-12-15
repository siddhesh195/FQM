from apscheduler.schedulers.gevent import GeventScheduler
import datetime
from app.helpers import get_number_of_active_tickets_cached, get_number_of_active_tickets_office_cached, get_number_of_active_tickets_task_cached
import app.database as data

scheduler = GeventScheduler()

def init_scheduler(app, socketio):

    def active_tickets():
        with app.app_context():
            active_tickets_number= get_number_of_active_tickets_cached()
            
            socketio.emit("active_tickets", {"all_active_tickets": active_tickets_number})

    def active_tickets_office():
        with app.app_context():
            offices = data.Office.query.all()
            offices_ids = [office.id for office in offices]
            active_tickets_by_office_id = {}
            active_tickets_by_task_id = {}
            for office_id in offices_ids:
                office_active_tickets = get_number_of_active_tickets_office_cached(office_id)
                active_tickets_by_office_id[office_id] = office_active_tickets
            
            task_ids_of_each_office_id = {}
            for office in offices:
                task_ids_of_each_office_id[office.id] = []
                for task in office.tasks:
                    task_ids_of_each_office_id[office.id].append(task.id)

            for office_id, task_ids in task_ids_of_each_office_id.items():
                active_tickets_by_task_id[office_id] = {}
                for task_id in task_ids:
                    task_active_tickets = get_number_of_active_tickets_task_cached(office_id=office_id, task_id=task_id)
                    active_tickets_by_task_id[office_id][task_id] = task_active_tickets
            

            
            socketio.emit("active_tickets_by_office_and_task_id", {"active_tickets_by_office_id": active_tickets_by_office_id,
                                                           "active_tickets_by_task_id": active_tickets_by_task_id})
    

    scheduler.add_job(active_tickets, "interval", seconds=5)
    scheduler.add_job(active_tickets_office, "interval", seconds=5)
    
    scheduler.start()
