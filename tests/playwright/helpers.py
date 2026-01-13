from playwright.sync_api import Page, expect
import re

def login(page: Page):
    page.goto("http://localhost:8001/")

    # Index page loaded
    expect(page.locator("h1", has_text="Digital Queue Management System")).to_be_visible()

    user_header = page.locator("h2.u")

    # Case 1: already authenticated
    if user_header.is_visible():
        # Clicking Login should navigate (not open modal)
        page.locator("a:has-text('Login')").click()
        expect(page.locator("body")).to_contain_text("Management")
        return

    # Case 2: not authenticated → modal login
    page.locator("a:has-text('Login')").click()

    # Modal must appear
    expect(page.locator("#upd")).to_be_visible()

    page.fill("input[name='name']", "Admin")
    page.fill("input[name='password']", "password")

    page.locator("#fm button[type='submit']").click()

    # Successful login proof
   
    expect(page.locator("body")).to_contain_text("Management")

def create_office(page: Page, office_name: str):
    page.click("text=Add new office")
    office_name = "Playwright Office"
    page.fill("input[name='name']", office_name)

    prefix_select = page.locator("select[name='prefix']")

    # Get all available option values
    options = prefix_select.locator("option")
    count = options.count()

    assert count > 0

    # Pick the first valid prefix
    prefix_value = options.nth(0).get_attribute("value")

    prefix_select.select_option(prefix_value)

    page.get_by_role("button", name="Add office").click()

    # Assert Swal is visible
    swal = page.locator(".swal2-popup")
    expect(swal).to_be_visible()

    # Assert message text
    try:
        expect(swal).to_contain_text("Office added successfully")

    finally:
        # Click OK
        page.locator(".swal2-confirm").click()
        # Assert Swal closed
        expect(swal).not_to_be_visible()

def delete_office(page: Page, office_name: str):
    page.click("text=Manage Home")
    page.get_by_role("button", name="Offices Management").click()
    search_input = page.get_by_placeholder("Search offices...")
    
    search_input.type(office_name)
    
   
    page.locator(".delete-office-link").click()
    
    #handle sweetalert2 confirm
    swal_confirm = page.locator(".swal2-popup")
    expect(swal_confirm).to_be_visible()
    swal_yes = swal_confirm.locator(".swal2-confirm")
    expect(swal_yes).to_be_visible()
    swal_yes.click()

    # confirm office deleted swal
    swal_success = page.locator(".swal2-popup")
    expect(swal_success).to_be_visible()
    
    expect(swal_success).to_contain_text("Office deleted successfully")
    #close swal
    swal_success.locator(".swal2-confirm").click()



def open_office(page: Page, office_name: str):
    office_span = page.locator(f'span[title="{office_name}"]')

    expect(office_span).to_be_visible()

    office_link = office_span.locator("xpath=ancestor::a")
    office_link.click()

    office_panel = (
        office_link
        .locator("xpath=ancestor::li")
        .locator("div.panel-collapse")
    )

    expect(office_panel).to_be_visible()

    return office_panel

def add_task(page: Page, task_name: str, office_name: str):
    truncated = office_name[:8]

    office_span =office_span = page.locator("span[title]").filter(has_text=truncated)
    expect(office_span).to_have_attribute("title", office_name)

    office_link = office_span.locator("xpath=ancestor::a")

    office_link.click()

    office_li = office_link.locator("xpath=ancestor::li")

    office_panel = office_li.locator("div.panel-collapse")

    expect(office_panel).to_be_visible()

    office_panel.get_by_role("link",name="Add new task").click()

    task_name = f"Playwright Task for {office_name}"

    page.fill("input[name='name']", task_name)

    page.get_by_role("button", name="Add task").click()

    # Assert Swal is visible
    swal = page.locator(".swal2-popup")
    expect(swal).to_be_visible()
    
    #close the swal
    page.locator(".swal2-confirm").click()

def open_touch_screen_for_office(page: Page, office_name: str, task_name: str):
    # Open Screens dropdown
    page.locator('a.dropdown-toggle:has-text("Screens")').click()

    touch_link = page.locator(
        f'//li[contains(@class,"dropdown-header") and contains(., "{office_name}")]'
        '/following-sibling::li[1]//a[contains(., "Touch screen")]'
    )

    expect(touch_link).to_be_visible()

    # Capture NEW TAB
    with page.context.expect_page() as p:
        touch_link.click()

    touch_page = p.value
    touch_page.wait_for_load_state()

    return touch_page


def create_new_token(touch_page,task_name: str, office_name: str):
    # Build full task name
    full_task_name = f"{task_name} for {office_name}"

    # Click task ON THE NEW PAGE
    task_link = touch_page.get_by_role("button", name=full_task_name)
    expect(task_link).to_be_visible()
    task_link.click()

    swal = touch_page.locator(".swal2-popup.custom-big-swal")
    expect(swal).to_be_visible()

    text = touch_page.locator(".swal2-html-container").inner_text()

    match = re.search(r"\b([A-F0-9]{8})\b", text)
    assert match, f"No token found in Swal message: {text}"

    token = match.group(1)

    #close swal alert
    touch_page.locator(".swal2-confirm").click()
    expect(swal).not_to_be_visible()

    return token

def check_token_in_scroll_content(display_page, token: str):
    scroll_content = display_page.locator(".scroll-content")
    expect(scroll_content).to_be_visible()
    expect(scroll_content).to_contain_text(token)

def check_token_in_pulled_table(display_page: Page, token: str):
    table = display_page.locator("table.tickets-table")
    expect(table).to_be_visible()

    # Look for any cell containing the token
    token_cell = table.locator("td", has_text=token)
    expect(token_cell).to_be_visible()


def open_display_screen_for_office(page: Page, office_name: str):
    # Open Screens dropdown
    page.locator('a.dropdown-toggle:has-text("Screens")').click()

    display_link = page.locator(
        f'//li[contains(@class,"dropdown-header") and contains(., "{office_name}")]'
        '/following-sibling::li[2]//a[contains(., "Display screen")]'
    )

    expect(display_link).to_be_visible()

    # Capture NEW TAB
    with page.context.expect_page() as p:
        display_link.click()

    display_page = p.value
    display_page.wait_for_load_state()

    return display_page


    
def open_office_tickets(office_panel):
    all_tickets_link = office_panel.get_by_role(
        "link",
        name="All tickets"
    )

    expect(all_tickets_link).to_be_visible()
    all_tickets_link.click()

def get_ticket_row(page: Page, token: str):
    # row that contains the token in any <td>
    row = page.locator("tbody tr", has=page.get_by_text(token))
    expect(row).to_be_visible()
    return row

def expect_sweetalert_success(page: Page, token: str):
    alert = page.locator(".swal2-popup")

    expect(alert).to_be_visible()

    # Assert message contains token
    expect(alert).to_contain_text(f"Successfully pulled ticket: {token}")

    # Click OK / Confirm
    confirm_button = alert.locator(".swal2-confirm")
    expect(confirm_button).to_be_visible()
    confirm_button.click()

    # Ensure alert disappears
    expect(alert).to_be_hidden()

def pull_a_token_and_assert(page,row,status_badge, token: str):
    # Click Pull
    row.locator("a.pull_ticket").click()

    # ✅ FIRST: handle SweetAlert
    expect_sweetalert_success(page, token)

    # ✅ THEN: assert UI state
    expect(status_badge).to_contain_text("Is Pulled")


def assert_token_present(page: Page,display_page: Page | None, token: str,pull:bool=False):
    # Ensure we're on the tickets page
    expect(page.get_by_placeholder("Search tickets...")).to_be_visible()

    search_input = page.get_by_placeholder("Search tickets...")
    search_input.fill("")      # clear first
    search_input.fill(token)   # type token

    # Vue debounce / reactivity safety
    page.wait_for_timeout(300)

    # Get the ticket row
    row = get_ticket_row(page, token)
    status_badge = row.locator(".status-badge")
    expect(status_badge).to_contain_text("Not Pulled")

    

    if pull:
        check_token_in_scroll_content(display_page, token)
        #pull and assert in UI where ticket is pulled
        pull_a_token_and_assert(page, row, status_badge, token)

        #assert in pulled table in display page
        check_token_in_pulled_table(display_page, token)
        
    
def reset_current_office(page: Page,office_name: str):
    reset_button = page.get_by_role("button", name="Reset this Office")
    expect(reset_button).to_be_visible()
    reset_button.click()

    # Handle SweetAlert2 confirm dialog
    swal_confirm_popup = page.locator(".swal2-popup")
    expect(swal_confirm_popup).to_be_visible()
    
    # Click "Yes" button to confirm
    swal_yes_button = page.locator(".swal2-confirm")
    expect(swal_yes_button).to_be_visible()
    swal_yes_button.click()

    # Handle SweetAlert2 success message
    swal_success_popup = page.locator(".swal2-popup")
    expect(swal_success_popup).to_be_visible()

    # Optional but recommended assertion
    expect(swal_success_popup).to_contain_text(f"Office {office_name} has been reset")

    # Close SweetAlert
    page.locator(".swal2-confirm").click()
    expect(swal_success_popup).not_to_be_visible()

    