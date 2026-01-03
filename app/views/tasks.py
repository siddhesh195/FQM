from flask import Blueprint, flash, jsonify, redirect, url_for, render_template
from flask_login import login_required
from app.forms.manage import TaskForm
from flask_login import current_user

from app.helpers import get_or_reject, is_operator, is_office_operator, reject_setting
import app.database as data
from app.middleware import db
from app.utils import ids

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

    print(office.id,'office_id')
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
    ''' to add a task '''
    if current_user.role_id!=1:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403


    form = TaskForm()

    if form.validate_on_submit():
        if data.Task.query.filter_by(name=form.name.data).first() is not None:
            return jsonify({'status': 'error', 'message': 'Task with this name already exists'})

        task = data.Task(form.name.data, form.hidden.data)
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