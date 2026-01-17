


from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.forms.adminstrate import UserForm2
import app.database as data
from app.middleware import db

administrate2 = Blueprint('administrate2', __name__)


def check_duplicate_user_name(new_name):
    existing_user = data.User.query.filter_by(name=new_name).first()
    return existing_user is not None



@administrate2.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):

    if current_user.role_id!=1:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403
    
    form = UserForm2()
    user = data.User.get(user_id)

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    if form.validate_on_submit():
        new_user_name = form.name.data
        
        if new_user_name:
            new_user_name = new_user_name.strip()
            if len(new_user_name) == 0:
                return jsonify({'status': 'error', 'message': 'You entered empty name'}), 400
            if check_duplicate_user_name(new_user_name) and new_user_name != user.name:
                return jsonify({'status': 'error', 'message': 'User name already exists'}), 400
            
            user.name = new_user_name
            
        if form.role.data:
            user.role_id = form.role.data

            # add as an operator in role id is 3
            if form.role.data == 3:
                
                operator = data.Operators.get(id=user.id)
                if not operator:
                    db.session.add(data.Operators(user.id,form.offices.data))
                else:
                    operator.office_id = form.offices.data
            else:
                to_delete = data.Operators.get(user.id)

                if to_delete is not None:
                    db.session.delete(to_delete)
        if form.password.data:
            user.password = form.password.data
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'User updated successfully'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid form data'}), 400
             

    
    

    

