from app.middleware import gtranslator
import uuid
from app.database import User

def get_translation(text, language):
    """Translate text to the specified language using gtranslator."""

    translated = gtranslator.translate(text, dest=[language])

    return translated

def generate_token_for_task(task, office):
    # Option A: short random token (safe, no race). Good if token doesn't have to be monotonic.
    
    return uuid.uuid4().hex[:8].upper()


def process_all_pulled_tickets(all_pulled_tickets):
    pulled_list = []

    for ticket in (all_pulled_tickets or [])[:10]:
        try:
            print(ticket.status,"ticket status")
            user = User.query.filter_by(id=ticket.pulledBy).first()
            pulled_by_name = user.name if user else "Unknown"
        except Exception as e:
            pulled_by_name = "Error"
            print(e)

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
