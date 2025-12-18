import pytest

class MockUser:
        def __init__(self):
            self.role_id = 1  # Admin role for testing

@pytest.mark.usefixtures("c")
def test_analytics_rules_home(c,monkeypatch):

    
    mock_user = MockUser()
    monkeypatch.setattr('app.views.analytics_rules.current_user', mock_user)
    url = '/analytics_rules'
    resp = c.get(url)
    assert resp.status_code == 200
    assert b"Analytics Rules" in resp.data


@pytest.mark.usefixtures("c")
def test_update_task_threshold(c,monkeypatch):

    mock_user = MockUser()
    monkeypatch.setattr('app.views.analytics_rules.current_user', mock_user)
    url = '/get_all_tasks_thresholds'
    resp = c.get(url)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)  # Assuming there are tasks in the database
    thresholds = {}

    for task in data:
        thresholds[task['name']] = task['threshold']
    task_to_update = data[0]['name']

    if thresholds[task_to_update] is None:
        thresholds[task_to_update] = 0
    
    new_threshold = thresholds[task_to_update] + 10

    update_url = '/update_task_threshold'
    resp = c.post(update_url, json={
        'task_name': task_to_update,
        'new_threshold': new_threshold
    })
    assert resp.status_code == 200
    resp_data = resp.get_json()
    assert resp_data['message'] == 'Threshold updated successfully'

    url2 = '/get_all_tasks_thresholds' 
    resp2 = c.get(url2)
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    task_found = False
    for task in data2:
        if task['name'] == task_to_update:
            assert task['threshold'] == new_threshold
            task_found = True
            break

    assert task_found