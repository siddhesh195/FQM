from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
import app.database as data
from app.middleware import db
from app.helpers2 import to_bool


manage_app2 = Blueprint('manage_app2', __name__)


@manage_app2.route('/manage_home')
@login_required
def manage_home():
    
    
    return render_template ('manage_home.html',title="Management Home")


@manage_app2.route('/get_all_tasks', methods=['GET'])
@login_required
def get_all_tasks():

    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    tasks = data.Task.query.all()
    task_office_names={}
    for task in tasks:
       
        task_offices = task.offices
        task_office_name_list = []
        for task_office in task_offices:
            task_office_name_list.append(task_office.name)
        task_office_names[task.id] = task_office_name_list
    
    
    tasks_list = [{'id': task.id, 'name': task.name, 'hidden': task.hidden, 'offices': task_office_names.get(task.id, [])} for task in tasks]
    return jsonify({'status': 'success', 'tasks': tasks_list})

@manage_app2.route('/modify_task', methods=['POST'])
@login_required
def modify_task():
    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    task_id = request.json.get('task_id',None)

    if not task_id:
        return jsonify({'status': 'error', 'message': 'Task ID not provided'})
    json_body= request.get_json()

    taskName= json_body.get('taskName',None)
    status= json_body.get('status',None)

    

    task = data.Task.query.get(task_id)
    if not task:
        return jsonify({'status': 'error', 'message': 'Task not found'})
    
    if status is not None:
        status = to_bool(status)
        task.hidden = status
        db.session.commit()
   

    return jsonify({'status': 'success', 'message': f'Task {task.name} status updated to {status}'})


