import pytest

pytest.skip(
    "Skipping long and less critical test",
    allow_module_level=True
)

from playwright.sync_api import Page

from helpers import login, create_office, open_office, delete_office, open_office_tickets, open_touch_screen_for_office
from helpers import add_task
from helpers import reset_current_office

from helpers2 import create_multiple_tokens, assert_multiple_tokens, assert_all_tickets_count, pull_office_specific_tickets

raise_office_creation_exception=False
raise_task_creation_exception=False
raise_display_screen_exception=True
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
        assert_multiple_tokens(page, token_list)
    except Exception as e:
        if raise_office_tickets_exception:
            raise Exception(e)
        
    try:
        assert_all_tickets_count(page,number_of_tokens)
    except Exception as e:
        if raise_office_tickets_exception:
            raise Exception(e)
        
   
    try:
        pull_office_specific_tickets(page,number_to_pull=number_of_tokens, tickets_count=number_of_tokens, office_name=office_name)
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

 

    