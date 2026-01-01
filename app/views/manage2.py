from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
import app.database as data
from app.middleware import db
from app.helpers2 import to_bool


manage_app2 = Blueprint('manage_app2', __name__)


@manage_app2.route('/manage_home')
@login_required
def manage_home():
    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    
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
    
    if taskName is not None:
        task.name = taskName
        db.session.commit()
   

    return jsonify({'status': 'success', 'message': f'Task {task.name} status updated to {status}'})

@manage_app2.route('/delete_a_task', methods=['POST'])
@login_required
def delete_a_task():
    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    task_id = request.json.get('task_id',None)

    if not task_id:
        return jsonify({'status': 'error', 'message': 'Task ID not provided'})
    
    task = data.Task.query.get(task_id)
    if not task:
        return jsonify({'status': 'error', 'message': 'Task not found'})
    
    db.session.delete(task)
    db.session.commit()

    return jsonify({'status': 'success', 'message': f'Task {task.name} deleted successfully'})



@manage_app2.route('/get_all_offices', methods=['GET'])
@login_required
def get_all_offices():

    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    offices = data.Office.query.all()
    
    offices_list = [{'id': office.id, 'name': office.name} for office in offices]
    return jsonify({'status': 'success', 'offices': offices_list})

@manage_app2.route('/modify_office', methods=['POST'])
@login_required
def modify_office():
    if current_user.role_id != 1:
        return jsonify({'status': 'error', 'message': 'Unauthorized'})
    office_id = request.json.get('office_id',None)

    if not office_id:
        return jsonify({'status': 'error', 'message': 'Office ID not provided'})
    json_body= request.get_json()

    officeName= json_body.get('officeName',None)
    

    office = data.Office.query.get(office_id)
    if not office:
        return jsonify({'status': 'error', 'message': 'Office not found'})
    

    if officeName is not None:
        office.name = officeName
        db.session.commit()
   

    return jsonify({'status': 'success', 'message': f'Office {office.name} updated successfully'})