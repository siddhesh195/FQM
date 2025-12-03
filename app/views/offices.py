from flask import Blueprint,render_template, jsonify
from flask_login import login_required
from app.helpers import reject_operator

import app.database as data

from app.constants import TICKET_ORDER_NEWEST_PROCESSED


offices = Blueprint('offices', __name__)


@offices.route('/all_offices_vue', methods=['GET', 'POST'])
@login_required
@reject_operator
def offices_home():

    offices=data.Office.query
    operators=data.Operators.query
    tasks=data.Task
    
    return render_template('all_offices_vue.html', page_title='Offices', offices=offices, operators=operators, tasks=tasks)

@offices.route('/all_offices_tickets', methods=['GET', 'POST'])
@login_required
@reject_operator
def all_offices_tickets():
    order_by = TICKET_ORDER_NEWEST_PROCESSED
    tickets = data.Serial.all_clean()\
                         .order_by(*data.Serial.ORDERS.get(order_by, []))
    
    tickets_data=[]


    for ticket in tickets:
        ticket_task_id = ticket.task_id
        task = data.Task.query.filter_by(id=ticket_task_id).first()
        task_name= task.name if task else 'N/A'
        ticket_office_id = ticket.office_id 
        office = data.Office.query.filter_by(id=ticket_office_id).first()
        office_name= office.name if office else 'N/A'
        pulled_by = data.User.query.filter_by(id=ticket.pulledBy).first()
        pulled_by_name = pulled_by.name if pulled_by else 'N/A'
        
        ticket_dict={
            'name': ticket.name,
            'status': ticket.status,
            'timestamp': ticket.timestamp,
            'office_name': office_name,
            'task_name': task_name,
            'pulled_by': pulled_by_name,
            'number': ticket.number,
            'pulled': ticket.p
        }
        tickets_data.append(ticket_dict)

   

    return jsonify(tickets_data)
    