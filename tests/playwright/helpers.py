from playwright.sync_api import Page, expect
import re

def login(page: Page):
    # Go to your Flask app
    page.goto("http://localhost:8001/")

    # Assert text is present anywhere on the page
    expect(page.locator("text=Digital Queue Management System")).to_be_visible()
    page.click("text=Login")
    

    expect(page.locator("#upd")).to_be_visible()

    page.fill("input[name='name']", "Admin")
    page.fill("input[name='password']", "admin")

    # Submit the login form
    page.click("#fm button[type='submit']")



    expect(page.locator("body")).to_contain_text(
        "Management"
    )

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
    def handle_dialog(dialog):
        assert dialog.type == "confirm"
        assert "delete this office" in dialog.message
        dialog.accept()

    page.once("dialog", handle_dialog)
   
    page.locator(".delete-office-link").click()
    def handle_alert(dialog):
        assert dialog.type == "alert"
        assert "office deleted successfully" in dialog.message.lower()
        dialog.accept()

    page.once("dialog", handle_alert)


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

    # Build full task name
    full_task_name = f"{task_name} for {office_name}"

    # Click task ON THE NEW PAGE
    task_link = touch_page.get_by_role("link", name=full_task_name)
    expect(task_link).to_be_visible()
    task_link.click()

    swal = touch_page.locator(".swal2-popup.custom-big-swal")
    expect(swal).to_be_visible()

    text = touch_page.locator(".swal2-html-container").inner_text()

    match = re.search(r"\b([A-F0-9]{8})\b", text)
    assert match, f"No token found in Swal message: {text}"

    token = match.group(1)

    #close the page
    touch_page.close()

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


def open_display_screen_for_office(page: Page, office_name: str,token: str=None, scroll: bool=False, pulled_table: bool=False):
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
    if scroll:
        check_token_in_scroll_content(display_page, token)
    if pulled_table:
        check_token_in_pulled_table(display_page, token)

    #close the page
    if scroll:
        return display_page
    else:
        display_page.close()

    
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

def assert_token_present(page: Page, token: str):
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

    # Click Pull
    row.locator("a.pull_ticket").click()

    # ✅ FIRST: handle SweetAlert
    expect_sweetalert_success(page, token)

    # ✅ THEN: assert UI state
    expect(status_badge).to_contain_text("Is Pulled")
    

def reset_current_office(page: Page,office_name: str):
    def handle_confirm(dialog):
        assert dialog.type == "confirm"
        assert "reset this office" in dialog.message
        dialog.accept()

    page.once("dialog", handle_confirm)

    reset_button = page.get_by_role("button", name="Reset this Office")
    expect(reset_button).to_be_visible()
    reset_button.click()

    # 3️⃣ Handle SweetAlert2 success message
    swal = page.locator(".swal2-popup")
    expect(swal).to_be_visible()

    # Optional but recommended assertion
    expect(swal).to_contain_text(f"Office {office_name} has been reset")

    # 4️⃣ Close SweetAlert
    page.locator(".swal2-confirm").click()
    expect(swal).not_to_be_visible()

    