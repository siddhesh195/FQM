from playwright.sync_api import Page, expect
from helpers import create_new_token, assert_token_present, open_display_screen_for_office


def create_multiple_tokens(number,page, office_name, task_name):

    token_list = []

    for _ in range(number):
        token = create_new_token(page, task_name, office_name)
        token_list.append(token)
    page.close()
    return token_list

def assert_multiple_tokens(page:Page,token_list:list, pull:bool=False,open_display:bool=False):
    display_page = None
    if open_display:
        display_page = open_display_screen_for_office(page=page, office_name="Playwright Office")
    for token in token_list:
        assert_token_present(page=page,display_page=display_page, token=token, pull=pull)
    
    # Close display page
    if display_page:
        display_page.close()


def assert_all_tickets_count(page:Page, expected_count:int):
    all_tickets_count_locator = page.locator("#all_tickets_count")
    expect(all_tickets_count_locator).to_have_text(str(expected_count))

def pull_any_office_tickets(page:Page, number_to_pull:int,tickets_count:int):

    expected_count_after_pull = tickets_count
    for _ in range(number_to_pull):
        expected_count_after_pull = expected_count_after_pull -1
        pull_any_office_ticket_link = page.locator("#pull_any_office_ticket")
        expect(pull_any_office_ticket_link).to_be_visible()
        pull_any_office_ticket_link.click()

        #confirm swal popup
        swal_confirm_button = page.locator(".swal2-confirm")
        expect(swal_confirm_button).to_be_visible()
        swal_confirm_button.click()
        #wait for swal to disappear
        expect(swal_confirm_button).not_to_be_visible()
        assert_all_tickets_count(page, expected_count_after_pull)

    return

def open_users_screen(page: Page):
    # Open Screens dropdown
    page.locator('a.dropdown-toggle:has-text("Administration")').click()

    users_link = page.locator(
        f'//li[contains(@class,"dropdown-header") and contains(., "Users")]'
        '/following-sibling::li[1]//a[contains(., "All users")]'
    )

    expect(users_link).to_be_visible()


    users_link.click()
    
    page.wait_for_load_state()

    return page

def go_to_add_user_screen(page: Page):
    add_user_link = page.locator("#add_user_link")
    expect(add_user_link).to_be_visible()
    add_user_link.click()
    page.wait_for_load_state()
    return page

def delete_user(page: Page, username: str):
    user_row = page.locator(
        f'//div[contains(@class,"row") and contains(@class,"well")]'
        f'[.//strong[contains(., "{username}")]]'
    )

    # Click trash icon
    user_row.locator('.fa-trash').click()

    # Confirm modal
    confirm_btn = page.get_by_role("button", name="Yes")
    expect(confirm_btn).to_be_visible()
    confirm_btn.click()

    page.wait_for_load_state()

def fill_add_user_form(page: Page,*,name: str,password: str,role: int,office_id: int | None = None,):
    # Name
    page.fill("#name", name)

    # Password
    page.fill("#password", password)

    # Role (SelectField, coerce=int)
    page.select_option("#role", str(role))

    # Offices field only appears for operator (role == 3)
    if role == 3:
        offices_container = page.locator(".offices")
        offices_container.wait_for(state="visible")

        assert office_id is not None, "office_id required for operator"
        page.select_option("#offices", str(office_id))
        
   
    page.locator("#add_user_button").click()
