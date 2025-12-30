
import time
from playwright.sync_api import Page, expect

from helpers import login, create_office, open_office, delete_office, open_office_tickets, open_touch_screen_for_office
from helpers import add_task
from helpers import assert_token_present, reset_current_office, open_display_screen_for_office

from helpers import check_token_in_pulled_table

raise_office_creation_exception=False
raise_task_creation_exception=False
raise_display_screen_exception=True
raise_office_open_exception=True
raise_office_tickets_exception =True
raise_office_delete_exception=True

def test_office_add_delete(page: Page):
    
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
    token=None
    try:
        token= open_touch_screen_for_office(page, office_name, task_name)
        
    except Exception as e:
        if raise_office_open_exception:
            raise Exception(e)
    if not token:
        raise Exception("Token not retrieved from touch screen")
    office_panel=None
    display_page=None
    try:
        display_page = open_display_screen_for_office(page, office_name,token,scroll=True)
        
    except Exception as e:
        if raise_display_screen_exception:
            raise Exception(e)
    if not display_page:
        raise Exception("Display page not opened")
    
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
        assert_token_present(page, token)
    except Exception as e:
        if raise_office_tickets_exception:
            raise Exception(e)
        
    try:
        check_token_in_pulled_table(display_page, token)
        
    except Exception as e:
        if raise_display_screen_exception:
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

 

    