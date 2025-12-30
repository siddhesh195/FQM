from helpers import login
from playwright.sync_api import Page
from helpers2 import open_users_screen
from helpers3 import delete_all_users, reset_and_delete_all_offices


def test_reset_everything(page: Page):
    login(page)

    try:
        open_users_screen(page)
        delete_all_users(page)
    except Exception as e:
        raise Exception(e)
    
    #go to index page
    login(page)

    page.locator('#da2 a').click()

    reset_and_delete_all_offices(page)
    

    

    