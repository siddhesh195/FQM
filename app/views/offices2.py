from flask import Blueprint, jsonify, request

from flask_login import current_user, login_required

import app.database as data
from app.middleware import db

offices2 = Blueprint('offices2', __name__)


@offices2.route('/delete_an_office', methods=['POST'])
@login_required
def delete_an_office():
    ''' Delete an office by ID.

    Returns
    -------
        response: JSON
            JSON with the result of the operation.
    '''
    if current_user.role_id != 1:
    
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    office_id = request.json.get('office_id')

    if not office_id:
        return jsonify({'status': 'error', 'message': 'Office ID is required'}), 400

    office = data.Office.query.get(office_id)

    if not office:
        return jsonify({'status': 'error', 'message': 'Office not found'}), 404

    #if office has tickets cannot delete
    all_office_tickets = data.Serial.all_office_tickets(office_id=office.id).all()
    if all_office_tickets:
        
        return jsonify({'status': 'error', 'message': 'Cannot delete office with active tickets'}), 200
    
    try:
        #if any tasks are assigned only to this office, they should be deleted as well
        tasks = list(office.tasks)
        for task in tasks:
            if len(task.offices) == 1:
                db.session.delete(task)
        db.session.delete(office)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Office deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500




