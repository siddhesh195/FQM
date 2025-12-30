from playwright.sync_api import Page
 
from helpers import create_office, delete_office, login
from helpers2 import fill_add_user_form, open_users_screen,go_to_add_user_screen,delete_user



def test_add_delete_office_operator(page: Page):
    login(page)
    try:
        create_office(page, "Playwright Office")
    except Exception as e:
        raise Exception(e)
    
    try:
        users_page = open_users_screen(page)
        add_user_page = go_to_add_user_screen(users_page)
        fill_add_user_form(
            add_user_page,
            name="playwright_user",
            password="playwright_pass",
            role=3,
            office_id=1,
        )
        updated_users_page = open_users_screen(page)
        delete_user(updated_users_page, "playwright_user")
    except Exception as e:
        raise Exception(e)
    
    if not users_page:
        raise Exception("Users page not opened")
    if not add_user_page:
        raise Exception("Add User page not opened")
    
    #delete office, cannot use page variable as users_page is opened
    # get new homescreen page first and pass it to delete_office, call login again
    login(page)

    try:
        delete_office(page, "Playwright Office")
    except Exception as e:
        raise Exception(e)
    
    # Close users page
    users_page.close()