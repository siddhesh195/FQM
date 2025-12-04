from flask import Blueprint,render_template, jsonify, request
from flask_login import login_required
from app.helpers import reject_operator

import app.database as data

from app.constants import TICKET_ORDER_NEWEST_PROCESSED,TICKET_WAITING

from app.helpers import is_operator,is_office_operator,is_common_task_operator,get_number_of_active_tickets_cached

from app.forms.manage import ProcessedTicketForm2

from app.middleware import db


offices = Blueprint('offices', __name__)


@offices.route('/all_offices_vue', methods=['GET', 'POST'])
@login_required
@reject_operator
def offices_home():

    offices=data.Office.query
    operators=data.Operators.query
    tasks=data.Task
    form = ProcessedTicketForm2()
    status_choices = [
        {"value": value, "label": label}
        for value, label in form.status.choices
    ]

    
    return render_template('all_offices_vue.html', page_title='Offices', offices=offices, operators=operators, tasks=tasks, form=form, status_choices=status_choices)

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
            'pulled': ticket.p,
            'office_id': ticket.office_id,
            'ticket_id': ticket.id
        }
        tickets_data.append(ticket_dict)


    return jsonify(tickets_data)


@offices.route('/pull_ticket',methods=['POST'])
@login_required
def pull_ticket():
    json_data = request.get_json()

    ticket_name = json_data.get("ticket_name")
    office_id = json_data.get("office_id")
    ticket_id = json_data.get("ticket_id")
    strict_pulling = data.Settings.get().strict_pulling
    office = data.Office.get(office_id)



    ticket= data.Serial.query.filter_by(id=ticket_id).first()
    if not ticket or ticket.on_hold:
        return jsonify({'status': 'error', 'message': 'Ticket not found'}), 404

    if ticket.p:
        return jsonify({'status': 'error', 'message': 'Ticket already pulled'})

    if is_operator() and not (is_office_operator(ticket.office_id)
                              if strict_pulling else
                              is_common_task_operator(ticket.task_id)):
        return jsonify({'status': 'error', 'message': 'Unauthorized to pull this ticket'})
    try:
        if ticket.pull((office or ticket.office).id):
            return jsonify({'status': 'success', 'message': f'Ticket {ticket_name} pulled successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Ticket could not be pulled. It may already be pulled'})
    except:
        return jsonify({'status': 'error', 'message': 'An error occurred while pulling the ticket'})


@offices.route('/update_token_details',methods=['POST'])
def update_token_details():

    form = ProcessedTicketForm2()
    json_data = request.get_json()
    ticket_name = json_data.get("ticket_name")
    status = json_data.get("status")
    ticket = data.Serial.query.filter_by(name=ticket_name).first()

    if not ticket:
        return jsonify({'status': 'error', 'message': 'Ticket not found'})
    try:
        if form.validate_on_submit():
            if status==TICKET_WAITING:
                ticket.p= False
            ticket.status=status
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Ticket updated successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Form validation failed'})
    except:
        return jsonify({'status': 'error', 'message': 'An error occurred while updating the ticket'})
    


@offices.route('/get_number_of_active_tickets', methods=['GET'])
@login_required
def get_all_active_tickets():
    active_tickets = get_number_of_active_tickets_cached()
    return jsonify({'active_tickets': active_tickets})



    
    