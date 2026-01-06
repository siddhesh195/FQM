from playwright.sync_api import Page, expect


def delete_all_users(page: Page):
    """
    Deletes all users except Admin from the Users page.
    Assumes the Users screen is already open.
    """

    # Click the "Delete all" button using data-target (language-safe)
    delete_all_btn = page.locator('[data-target="#dall"]')
    expect(delete_all_btn).to_be_visible()
    delete_all_btn.click()

    # Wait for confirmation modal
    modal = page.locator('#dall')
    expect(modal).to_be_visible()

    # Click "Yes" inside the modal
    yes_button = modal.get_by_role("button", name="Yes")
    expect(yes_button).to_be_visible()

    with page.expect_navigation():
        yes_button.click()

def _accept_js_confirm(page: Page):
    page.once("dialog", lambda d: d.accept())


def _accept_swal_confirm(page: Page):
    """
    Handles SweetAlert2 confirm dialog by clicking the Yes button.
    """
    swal_yes = page.locator(
        '.swal2-confirm'
    )
    expect(swal_yes).to_be_visible(timeout=10_000)
    swal_yes.click()


def _accept_swal(page: Page):
    """
    Handles SweetAlert (swal / swal2) OK button.
    """
    swal_ok = page.locator(
        '.swal-button, .swal2-confirm'
    )
    expect(swal_ok).to_be_visible(timeout=10_000)
    swal_ok.click()

def reset_and_delete_all_offices(page: Page):
    """
    Reset all offices, then delete all offices and tasks.
    Handles SweetAlert2 confirm + SweetAlert popups.
    """

    # ---------- Reset All Offices ----------
    reset_btn = page.locator("#resetAllOfficesBtn")
    expect(reset_btn).to_be_visible()
    reset_btn.click()

    # Accept SweetAlert2 confirm dialog
    _accept_swal_confirm(page)

    # Accept success message
    _accept_swal(page)

    # ---------- Delete All Offices & Tasks ----------
    delete_btn = page.locator("#deleteAllOfficesAndTasksBtn")
    expect(delete_btn).to_be_visible()
    delete_btn.click()

    # Accept SweetAlert2 confirm dialog
    _accept_swal_confirm(page)

    # Accept success message (after page reload)
    # Note: Page reloads after delete, so success message may not appear