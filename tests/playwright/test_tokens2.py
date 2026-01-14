from playwright.sync_api import Page

from helpers import login, create_office, open_office, delete_office, open_office_tickets, open_touch_screen_for_office
from helpers import add_task, close_all_swal
from helpers import reset_current_office
from tests.playwright.helpers2 import assert_multiple_tokens, create_multiple_tokens

raise_office_creation_exception=False
raise_task_creation_exception=False
raise_office_open_exception=True
raise_office_tickets_exception =True
raise_office_delete_exception=True

def test_create_and_pull_lot_of_tokens(page: Page):
    
    login(page)
    office_name = "Playwright Office"
    task_name = "Playwright Task"
    try:
        create_office(page, office_name)
    except Exception as e:
        if raise_office_creation_exception:
            raise Exception(e)
    try:
        add_task(page, task_name, office_name)
    except Exception as e:
        if raise_task_creation_exception:
            raise Exception(e)

    token_list=[]
    number_of_tokens=3
    try:
        touch_page = open_touch_screen_for_office(page, office_name, task_name)
        close_all_swal(page)
        token_list = create_multiple_tokens(number_of_tokens,touch_page, office_name, task_name)
        
    except Exception as e:
        if raise_office_open_exception:
            raise Exception(e)
   
    if not token_list or len(token_list)!=number_of_tokens:
        raise Exception("Multiple tokens not created")
    
    office_panel=None
    
    try:
        office_panel = open_office(page, office_name)
    except Exception as e:
        if raise_office_open_exception:
            raise Exception(e)
    if not office_panel:
        raise Exception("Office panel not opened")
    
    try:
        open_office_tickets(office_panel)
    except Exception as e:
        if raise_office_tickets_exception:
            raise Exception(e)
        
    try:
        assert_multiple_tokens(page=page, token_list=token_list, pull=True, open_display=True)
    except Exception as e:
        if raise_office_tickets_exception:
            raise Exception(e)
        
    try:
        reset_current_office(page, office_name)
    except Exception as e:
        if raise_office_tickets_exception:
            raise Exception(e)
    try:
        delete_office(page, office_name)
    except Exception as e:
        if raise_office_delete_exception:
            raise Exception(e)
    #wait for some time 
    page.wait_for_timeout(2000)

 

    
    