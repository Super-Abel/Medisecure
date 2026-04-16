import pytest
from playwright.sync_api import Page


@pytest.mark.django_db
@pytest.mark.e2e
def test_signup_page_loads(page: Page, live_server):
    print(f"DEBUG: live_server at {live_server.url}")
    page.goto(live_server.url + "/accounts/signup/")
    print(f"DEBUG: Page title: {page.title()}")
    assert "Inscription" in page.title()
