
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.database import Task
from app.middleware import db

analytics_rules = Blueprint('analytics_rules', __name__)


@analytics_rules.route('/analytics_rules')
@login_required
def analytics_rules_home():

    if current_user.role_id != 1:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    return render_template('analytics_rules.html', page_title='Analytics Rules')


@analytics_rules.route('/get_all_tasks_thresholds')
@login_required
def get_all_tasks():
    if current_user.role_id != 1:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    all_tasks = Task.get_all_tasks()
    

    tasks_data = [{'name': task.name, 'threshold': task.threshold} for task in all_tasks]

    return jsonify(tasks_data)


@analytics_rules.route('/update_task_threshold', methods=['POST'])
@login_required
def update_task_threshold():
    if current_user.role_id != 1:
        return jsonify({'error': 'Unauthorized access'}), 403
    data = request.get_json()
    task_name = data.get('task_name')
    new_threshold = data.get('new_threshold')

    task = Task.query.filter_by(name=task_name).first()
    if task:
        task.threshold = new_threshold
        db.session.commit()
        return jsonify({'message': 'Threshold updated successfully'}), 200
    else:
        return jsonify({'error': 'Task not found'}), 404