from app.middleware import gtranslator
import uuid
from app.database import User
from app.constants import TICKET_WAITING
from flask_login import current_user
from app.middleware import db
from datetime import datetime

def get_translation(text, language):
    """Translate text to the specified language using gtranslator."""

    translated = gtranslator.translate(text, dest=[language])

    return translated

def generate_token_for_task():
    # Option A: short random token (safe, no race). Good if token doesn't have to be monotonic.
    
    return uuid.uuid4().hex[:8].upper()


def process_all_pulled_tickets(all_pulled_tickets):
    pulled_list = []

    for ticket in (all_pulled_tickets or [])[:10]:
        try:
            user = User.query.filter_by(id=ticket.pulledBy).first()
            pulled_by_name = user.name if user else "Unknown"
        except Exception as e:
            pulled_by_name = "Error"
            continue
        if ticket.status != TICKET_WAITING:
            continue
       
        empty_text = 'Empty'
        
        pulled_list.append({
            'id': ticket.id,
            'name': ticket.name,
            'pulled_by': pulled_by_name,
            # pdt may be None; convert to ISO string for JSON
            'pdt': ticket.pdt.isoformat() if getattr(ticket, 'pdt', None) else None,
            'office': getattr(ticket.office, 'display_text', None) or empty_text,
            'task': getattr(ticket.task, 'name', None) or empty_text,
        })
    
    return pulled_list

def last_pulled_ticket_by_each_user(all_pulled_tickets):
    last_pulled_dict = {}

    for ticket in all_pulled_tickets or []:
        try:
            user = User.query.filter_by(id=ticket.pulledBy).first()
            pulled_by_name = user.name if user else "Unknown"
        except Exception as e:
            pulled_by_name = "Error"
            continue
        if ticket.status != TICKET_WAITING:
            continue
        
        if ticket.pulledBy not in last_pulled_dict or ticket.pdt > last_pulled_dict[ticket.pulledBy]['pdt']:
            last_pulled_dict[ticket.pulledBy] = {
                'id': ticket.id,
                'name': ticket.name,
                'pulled_by': pulled_by_name,
                'pdt': ticket.pdt,
                'office': getattr(ticket.office, 'display_text', None) or 'Empty',
                'task': getattr(ticket.task, 'name', None) or 'Empty',
            }
    
    return last_pulled_dict

def update_last_seen_helper():
    ''' adding the last time user logged in '''
    print("Updating last seen for user...")
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        print("Last seen updated to:", current_user.last_seen)
        db.session.add(current_user)
        db.session.commit()
