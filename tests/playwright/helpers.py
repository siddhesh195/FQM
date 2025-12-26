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

def open_office_tickets(office_panel):
    all_tickets_link = office_panel.get_by_role(
        "link",
        name="All tickets"
    )

    expect(all_tickets_link).to_be_visible()
    all_tickets_link.click()

def assert_token_present(page: Page, token: str):
    # Ensure we're on the tickets page
    expect(page.get_by_placeholder("Search tickets...")).to_be_visible()

    search_input = page.get_by_placeholder("Search tickets...")
    search_input.fill("")      # clear first
    search_input.fill(token)   # type token

    # Vue debounce / reactivity safety
    page.wait_for_timeout(300)

    # Assert token appears somewhere in table
    token_cell = page.get_by_role("cell", name=token)

    expect(token_cell).to_be_visible()
    

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

    