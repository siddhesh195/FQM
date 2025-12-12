from apscheduler.schedulers.gevent import GeventScheduler
import datetime
from app.helpers import get_number_of_active_tickets_cached, get_number_of_active_tickets_office_cached, get_number_of_active_tickets_task_cached

scheduler = GeventScheduler()

def init_scheduler(app, socketio):
    def active_tickets():
        with app.app_context():
            active_tickets_number= get_number_of_active_tickets_cached()
            
            socketio.emit("active_tickets", {"all_active_tickets": active_tickets_number})

    scheduler.add_job(active_tickets, "interval", seconds=5)
    scheduler.start()
