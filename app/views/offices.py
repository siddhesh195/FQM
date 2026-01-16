from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user

import app.database as data

from app.constants import TICKET_ORDER_NEWEST_PROCESSED,TICKET_WAITING,TICKET_PROCESSED, TICKET_ATTENDED

from app.helpers import is_operator,is_office_operator,is_common_task_operator,get_number_of_active_tickets_cached
from app.helpers import has_offices

from app.forms.manage import ProcessedTicketForm2

from app.middleware import db

from app.forms.manage import OfficeForm
from app.utils import remove_string_noise
from datetime import datetime
from app.helpers import reject_operator


offices = Blueprint('offices', __name__)


@offices.route('/all_offices_vue', methods=['GET', 'POST'],defaults={'o_id': None})
@offices.route('/all_offices_vue/<int:o_id>', methods=['GET', 'POST'])
@login_required
def offices_home(o_id=None):

    try:
        if not current_user.role_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized access'})
    except:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'})
    
    if not o_id and current_user.role_id!=1:
        return jsonify({'status': 'error', 'message': 'Office ID is required for Non Admins'}), 400

    if o_id and current_user.role_id!=1:
        office= data.Office.get(o_id)
        if not office:
            return jsonify({'status': 'error', 'message': 'Office not found'}), 404
        
        operator = data.Operators.query.filter_by(id=current_user.id).first()
        if operator.office_id != o_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized access to this office'}), 403
    
    user_name = current_user.name
    offices=data.Office.query
    operators=data.Operators.query
    tasks=data.Task
    form = ProcessedTicketForm2()
    status_choices = [
        {"value": value, "label": label}
        for value, label in form.status.choices
    ]
    
    
    return render_template('all_offices_vue.html', page_title='Offices', offices=offices, operators=operators, tasks=tasks, form=form, status_choices=status_choices,office_id=o_id, user_name=user_name)

@offices.route('/all_offices_tickets', methods=['GET', 'POST'])
@login_required
def all_offices_tickets():
    order_by = TICKET_ORDER_NEWEST_PROCESSED
    o_id = request.json.get("o_id") if request.is_json else None
    if o_id:
        tickets = data.Serial.all_clean().filter_by(office_id=o_id)\
                         .order_by(*data.Serial.ORDERS.get(order_by, []))
    else:
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

    if not office:
        return jsonify({'status': 'error', 'message': 'Office not found'})

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
        if ticket.pull((office).id):
            return jsonify({'status': 'success', 'message': f'Ticket {ticket_name} pulled successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Ticket could not be pulled. It may already be pulled'})
    except:
        return jsonify({'status': 'error', 'message': 'An error occurred while pulling the ticket'})


@offices.route('/update_token_details',methods=['POST'])
@login_required
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
            if ticket.status == status and ticket.status==TICKET_WAITING and not ticket.p:
                return jsonify({'status': 'error', 'message': 'Ticket is already in the desired status'})
            
            if (status ==TICKET_PROCESSED or status == TICKET_ATTENDED) and not ticket.p:
                return jsonify({'status': 'error', 'message': 'Ticket must be pulled before processing/attending'})
            if status == TICKET_PROCESSED and ticket.status!=TICKET_ATTENDED:
                return jsonify({'status': 'error', 'message': 'Ticket must be in process before processing'})

            if status==TICKET_WAITING:
                ticket.p= False
                ticket.timestamp2= None
                ticket.timestamp3= None

            if status==TICKET_PROCESSED:
                ticket.timestamp3= datetime.utcnow()
                
            if status==TICKET_ATTENDED:
                if not ticket.timestamp2:
                    ticket.timestamp2= datetime.utcnow()
                ticket.timestamp3= None

            ticket.status=status
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Ticket updated successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Form validation failed'})
    except:
        return jsonify({'status': 'error', 'message': 'An error occurred while updating the ticket'})
    


@offices.route('/get_number_of_active_tickets', methods=['GET'])
@login_required
@reject_operator
def get_all_active_tickets():
    active_tickets = get_number_of_active_tickets_cached()
    return jsonify({'active_tickets': active_tickets})



@login_required
@offices.route('/pull_next_ticket', methods=['POST'])
def pull_next_ticket():

    def operators_not_allowed():
        return jsonify({'status': 'error', 'message': 'Unauthorized to pull this ticket'})

    json_data = request.get_json()
    task_id = json_data.get("task_id")
    ofc_id = json_data.get("ofc_id")
    if not ofc_id:
        return jsonify({'status': 'error', 'message': 'Office ID is required'})

    settings = data.Settings.get()
    strict_pulling = settings.strict_pulling
    single_row = settings.single_row
    task = data.Task.get(0 if single_row else task_id)
    office = data.Office.get(0 if single_row else ofc_id)
    if not office:
        return jsonify({'status': 'error', 'message': 'Office not found'})
    global_pull = not bool(task_id and ofc_id)

    if global_pull:
        if not single_row and is_operator():
            return operators_not_allowed()
    
    if is_operator() and not (is_office_operator(ofc_id)
                                  if strict_pulling else
                                  is_common_task_operator(task.id)):
            return operators_not_allowed()
    next_ticket = data.Serial.get_next_ticket(task_id=task_id,
                                              office_id=ofc_id)
    if not next_ticket:
        return jsonify({'status': 'error', 'message': 'No tickets available to pull'})
    next_ticket.pull(office and office.id or next_ticket.office_id)
    return jsonify({'status': 'success', 'message': f'Ticket {next_ticket.name} pulled successfully',
                    'ticket_name': next_ticket.name,
                    'ticket_id': next_ticket.id,
                    'office_id': next_ticket.office_id})


@offices.route('/fetch_office_and_task_ids', methods=['GET'])
@login_required
def fetch_office_and_task_ids():
    offices = data.Office.query.all()
    tasks = data.Task.query.all()

    office_ids = [office.id for office in offices]
    task_ids = [task.id for task in tasks]

    return jsonify({'office_ids': office_ids, 'task_ids': task_ids})

@offices.route('/add_office', methods=['POST', 'GET'])
@login_required
def add_office():
    ''' add an office. '''
    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'})
    form = OfficeForm()
    
    
    if request.method == 'POST':

        if form.validate_on_submit():
            office_name = remove_string_noise(form.name.data or '',
                                      lambda s: s.startswith('0'),
                                      lambda s: s[1:]) or None
            office_name = office_name.strip() 
            
            if data.Office.query.filter_by(name=office_name).first():
                return jsonify({'status': 'error', 'message': 'Office name already exists'})
            
            
            db.session.add(data.Office(office_name, form.prefix.data.upper()))
            db.session.commit()
       
            return jsonify({'status': 'success', 'message': 'Office added successfully'})
        else:
            
            return jsonify({'status': 'error', 'message': 'Form validation failed'}), 400

    return render_template('office_add.html',
                           form=form,
                           page_title='Adding new office',
                           offices=data.Office.query,
                           tasks=data.Task,
                           operators=data.Operators.query,
                           navbar='#snb1',
                           hash='#da3',
                           serial=data.Serial.all_clean())

@offices.route('/reset_all_offices', methods=['POST'])
@login_required
def reset_all_offices():
    ''' reset all offices by removing all tickets. '''
    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403
    if not has_offices():
        return jsonify({'status': 'error', 'message': 'No offices to reset'})
    
    
    tickets = data.Serial.query.filter(data.Serial.number != 100)
    try:
        tickets.delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'All offices have been reset'})
    except:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'An error occurred while resetting offices'})

@offices.route('/delete_all_offices_and_tasks', methods=['POST'])
@login_required
def delete_all_offices_and_tasks():
    ''' delete all offices. '''
    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403
    if not has_offices():
        return jsonify({'status': 'error', 'message': 'No offices to delete'})
    
    if data.Serial.query.filter(data.Serial.number != 100).count():
        return jsonify({'status': 'error', 'message': 'Cannot delete offices with existing tickets. Please reset all offices first.'})
    
    try:
        
        data.Serial.query.delete(synchronize_session=False)
        offices = data.Office.query.all()
        
        # delete offices
        for office in offices:
            db.session.delete(office)
    
        data.Task.query.delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'All offices and Tasks have been deleted'})
    except:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'An error occurred while deleting offices'})
    
@offices.route('/reset_single_office', methods=['POST'])
@login_required
def reset_single_office():
    ''' reset a single office by removing all its tickets. '''

    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403

    json_data = request.get_json()
    office_id = json_data.get("office_id", None)
    if not office_id:
        return jsonify({'status': 'error', 'message': 'Office ID is required'}), 400
    
    if current_user.role_id != 1 and not is_office_operator(office_id):
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403
    
    
    office = data.Office.get(office_id)
    if not office:
        return jsonify({'status': 'error', 'message': 'Office not found'})
    
    tickets = data.Serial.query.filter_by(office_id=office_id).filter(data.Serial.number != 100)
    try:
        tickets.delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Office {office.name} has been reset'})
    except:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'An error occurred while resetting the office'})

