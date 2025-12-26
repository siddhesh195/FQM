from playwright.sync_api import Page, expect

from helpers import login, create_office, open_office, delete_office
from helpers import add_task

def test_office_add_delete(page: Page):
    
    login(page)
    office_name = "Playwright Office"
    task_name = "Playwright Task"
    try:
        create_office(page, office_name)
    except:
        pass
    try:
        add_task(page, task_name, office_name)
    except:
        pass
    try:
        open_office(page, office_name)
    except:
        pass
    try:
        delete_office(page, office_name)
    except:
        pass

    #wait for some time 
    page.wait_for_timeout(2000)

    