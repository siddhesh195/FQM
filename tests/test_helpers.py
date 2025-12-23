import pytest
import app.database as data
from app.helpers import get_number_of_active_tickets_cached


@pytest.mark.usefixtures("c")
def test_get_number_of_active_tickets_cached(c):

    current_active_tickets_count = get_number_of_active_tickets_cached()

    #pull a ticket to change active tickets count
    all_tickets = data.Serial.all_clean()

    ticket_to_pull =None
    for ticket in all_tickets:
        if not ticket.p:
            ticket_to_pull = ticket
            break
    if not ticket_to_pull:
        pytest.skip("No available ticket to pull for testing.")
    ticket_id = ticket_to_pull.id
    ticket_name = ticket_to_pull.name
    office_id = ticket_to_pull.office_id
    pull_url='/pull_ticket'
    pull_payload = {
        'ticket_id': ticket_id,
        'office_id': office_id,
        'ticket_name': ticket_name
    }
    pull_resp = c.post(pull_url,json=pull_payload)
    assert pull_resp.status_code == 200
    pull_json_response = pull_resp.get_json()
    assert pull_json_response['status'] == 'success'

    #Get active tickets count again
    new_current_active_tickets_count = get_number_of_active_tickets_cached()

    assert new_current_active_tickets_count == current_active_tickets_count - 1
