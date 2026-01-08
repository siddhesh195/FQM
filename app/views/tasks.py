from flask import Blueprint, flash, jsonify, redirect, url_for, render_template, request
from flask_login import login_required
from app.forms.manage import TaskForm
from flask_login import current_user

from app.helpers import get_or_reject, is_operator, is_office_operator, reject_operator, reject_setting, reject_no_offices
import app.database as data
from app.middleware import db
from app.utils import ids
from app.helpers2 import to_bool

tasks = Blueprint('tasks', __name__)



@tasks.route('/add_task_home/<int:o_id>', methods=['POST', 'GET'])
@login_required
@reject_setting('single_row', True)
@get_or_reject(o_id=data.Office)
def add_task_home(office):
    ''' task_add page '''
    form = TaskForm()
    
    try:
        if current_user.role_id !=1:
            flash('Error: only admins are allowed to access the page ', 'danger')
            return redirect(url_for('core.root'))
    except:
        flash('Error: only admins are allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    if is_operator() and not is_office_operator(office.id):
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    return render_template('task_add.html', form=form,
                           offices=data.Office.query,
                           serial=data.Serial.all_clean(),
                           tasks=data.Task,
                           operators=data.Operators.query,
                           navbar='#snb1', common=False,
                           dropdown='#dropdown-lvl' + str(office.id),
                           hash='#t3' + str(office.id),
                           page_title='Add new task',o_id=office.id)


@tasks.route('/add_task/<int:o_id>', methods=['POST', 'GET'])
@login_required
@get_or_reject(o_id=data.Office)
def add_task(office):
    ''' to add a task in office'''
    if current_user.role_id!=1:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403


    form = TaskForm()

    if form.validate_on_submit():
        task_name = form.name.data.strip()
        existing_tasks = data.Task.query.filter_by(name=task_name).all()
        if existing_tasks:
            existing_task_office_ids=[]
            for existing_task in existing_tasks:
                existing_task_office_ids.extend(ids(existing_task.offices))
            if office.id in existing_task_office_ids:
                return jsonify({'status': 'error', 'message': 'Task with this name already exists in this office'})
        
        task = data.Task(task_name, form.hidden.data)
        db.session.add(task)
        db.session.commit()

        if office.id not in ids(task.offices):
            task.offices.append(office)
            db.session.commit()

        initial_ticket = data.Serial.query.filter_by(task_id=task.id,
                                                     office_id=office.id,
                                                     number=100)\
                                          .first()

        if not initial_ticket:
            db.session.add(data.Serial(office_id=task.offices[0].id,
                                       task_id=task.id,
                                       p=True))
            db.session.commit()


        return jsonify({'status': 'success', 'message': 'Task added successfully'})
    else:
 
        return jsonify({'status': 'error', 'message': 'Form validation failed'})


@tasks.route('/add_common_task', methods=['POST'])
@login_required
@reject_operator
@reject_no_offices
def add_common_task():
    ''' Add a common task (JSON API) '''

    # Authorization (admins only, same intent as old route)
    if current_user.role_id != 1:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access'
        }), 403

    form = TaskForm(common=True)

    if not form.validate_on_submit():
        return jsonify({
            'status': 'error',
            'message': 'Form validation failed'
        }), 400

    task_name = form.name.data.strip()

    # Task name must be globally unique
    existing_task = data.Task.query.filter_by(name=task_name).first()
    if existing_task:
        return jsonify({
            'status': 'error',
            'message': 'Task name is already in use'
        }), 409

    # Validate that at least one office is selected
    offices = data.Office.query.all()
    selected_offices = [
        office for office in offices
        if form.get(f'check{office.id}') and form[f'check{office.id}'].data
    ]

    if not selected_offices:
        return jsonify({
            'status': 'error',
            'message': 'At least one office must be selected'
        }), 400

    # Create task
    task = data.Task(task_name, form.hidden.data)
    db.session.add(task)
    db.session.commit()

    # Associate offices
    for office in selected_offices:
        if office not in task.offices:
            task.offices.append(office)

    db.session.commit()

    # Create initial serial (number=100) for each associated office
    for office in task.offices:
        initial_ticket = data.Serial.query.filter_by(
            office_id=office.id,
            task_id=task.id,
            number=100
        ).first()

        if not initial_ticket:
            db.session.add(data.Serial(
                office_id=office.id,
                task_id=task.id,
                p=True
            ))

    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Common task added successfully',
        'task_id': task.id,
        'offices': [office.id for office in task.offices]
    }), 201

    
@tasks.route('/modify_task', methods=['POST'])
@login_required
def modify_task():
    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    task_id = request.json.get('task_id',None)

    if not task_id:
        return jsonify({'status': 'error', 'message': 'Task ID not provided'})
    json_body= request.get_json()

    taskName= json_body.get('taskName',None)
    if taskName is not None:
        taskName= taskName.strip()
    status= json_body.get('status',None)

    
    task = data.Task.query.get(task_id)
    if not task:
        return jsonify({'status': 'error', 'message': 'Task not found'})
    
    if status is not None:
        status = to_bool(status)
        task.hidden = status
        db.session.commit()
    
    if taskName is not None:
        #check for duplicate task name in the same offices
        existing_task = data.Task.query.filter_by(name=taskName).first()
        if existing_task and existing_task.id != task.id:
            existing_task_office_ids = ids(existing_task.offices)
            for office in task.offices:
                if office.id in existing_task_office_ids:
                    return jsonify({'status': 'error', 'message': 'Task with this name already exists in this office'})
        task.name = taskName
        db.session.commit()
   

    return jsonify({'status': 'success', 'message': f'Task {task.name} status updated to {status}'})