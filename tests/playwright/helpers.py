from playwright.sync_api import Page, expect

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


def open_office(page: Page, office_name: str):
    truncated = office_name[:8]

    office_span = page.locator("span[title]").filter(has_text=truncated)
    expect(office_span).to_have_attribute("title", office_name)

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