from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.helpers import reject_operator

import app.database as data

from app.constants import TICKET_ORDER_NEWEST_PROCESSED,TICKET_WAITING,TICKET_PROCESSED, TICKET_ATTENDED

from app.helpers import is_operator,is_office_operator,is_common_task_operator,get_number_of_active_tickets_cached
from app.helpers import get_number_of_active_tickets_office_cached, get_number_of_active_tickets_task_cached

from app.forms.manage import ProcessedTicketForm2

from app.middleware import db

from app.forms.manage import OfficeForm
from app.utils import remove_string_noise


offices = Blueprint('offices', __name__)


@offices.route('/all_offices_vue', methods=['GET', 'POST'],defaults={'o_id': None})
@offices.route('/all_offices_vue/<int:o_id>', methods=['GET', 'POST'])
@login_required
def offices_home(o_id=None):
    if not o_id and is_operator():
        return jsonify({'status': 'error', 'message': 'Office ID is required for operators'}), 400
    
    offices=data.Office.query
    operators=data.Operators.query
    tasks=data.Task
    form = ProcessedTicketForm2()
    status_choices = [
        {"value": value, "label": label}
        for value, label in form.status.choices
    ]
    office_ids=[]
    task_ids=[]
    all_tasks = tasks.query.all()
    for task in all_tasks:
        task_ids.append(task.id)
    if o_id:
        office_ids.append(o_id)
    else:
        try:
            all_offices = offices.all()
            for office in all_offices:
                office_ids.append(office.id)
        except:
            pass

    
    return render_template('all_offices_vue.html', page_title='Offices', offices=offices, operators=operators, tasks=tasks, form=form, status_choices=status_choices,office_id=o_id,
                           office_ids=office_ids, task_ids=task_ids)

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
            if (status ==TICKET_PROCESSED or status == TICKET_ATTENDED) and not ticket.p:
                return jsonify({'status': 'error', 'message': 'Ticket must be pulled before processing/attending'})

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
@reject_operator
def get_all_active_tickets():
    active_tickets = get_number_of_active_tickets_cached()
    return jsonify({'active_tickets': active_tickets})


@offices.route('/get_number_of_active_office_tickets', methods=['GET', 'POST'])
@login_required
def get_all_active_office_tickets():
    json_data = request.get_json()
    o_id = json_data.get("o_id") if request.is_json else None
    active_tickets = get_number_of_active_tickets_office_cached(o_id)
    return jsonify({'active_tickets': active_tickets})


@offices.route('/get_number_of_active_task_tickets', methods=['GET', 'POST'])
@login_required
def get_all_active_task_tickets():
    json_data = request.get_json()
    t_id = json_data.get("t_id")
    office_id = json_data.get("office_id")
    active_tickets = get_number_of_active_tickets_task_cached(task_id=t_id, office_id=office_id)
    return jsonify({'active_tickets': active_tickets})


@login_required
@offices.route('/pull_next_ticket', methods=['POST'])
def pull_next_ticket():

    def operators_not_allowed():
        return jsonify({'status': 'error', 'message': 'Unauthorized to pull this ticket'})

    json_data = request.get_json()
    o_id = json_data.get("o_id")
    ofc_id = json_data.get("ofc_id")

    settings = data.Settings.get()
    strict_pulling = settings.strict_pulling
    single_row = settings.single_row
    task = data.Task.get(0 if single_row else o_id)
    office = data.Office.get(0 if single_row else ofc_id)
    global_pull = not bool(o_id and ofc_id)

    if global_pull:
        if not single_row and is_operator():
            return operators_not_allowed()
    else:
        if not task:
            return jsonify({'status': 'error', 'message': 'Task not found'})
    if is_operator() and not (is_office_operator(ofc_id)
                                  if strict_pulling else
                                  is_common_task_operator(task.id)):
            return operators_not_allowed()
    next_ticket = data.Serial.get_next_ticket(task_id=o_id,
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
    office_name = remove_string_noise(form.name.data or '',
                                      lambda s: s.startswith('0'),
                                      lambda s: s[1:]) or None
    
    if request.method == 'POST':

        if form.validate_on_submit():
            if data.Office.query.filter_by(name=form.name.data).first():
                return jsonify({'status': 'error', 'message': 'Office name already exists'})
            
            
            db.session.add(data.Office(office_name, form.prefix.data.upper()))
            db.session.commit()
       
            return jsonify({'status': 'success', 'message': 'Office added successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Form validation failed'})

    return render_template('office_add.html',
                           form=form,
                           page_title='Adding new office',
                           offices=data.Office.query,
                           tasks=data.Task,
                           operators=data.Operators.query,
                           navbar='#snb1',
                           hash='#da3',
                           serial=data.Serial.all_clean())
