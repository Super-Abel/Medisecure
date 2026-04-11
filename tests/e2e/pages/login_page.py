from __future__ import annotations

from .base_page import BasePage


class LoginPage(BasePage):
    PATH = "/accounts/login/"

    def login(self, email: str, password: str) -> None:
        self._page.fill("input[name='login']", email)
        self._page.fill("input[name='password']", password)
        self._page.click("button[type='submit']")

    @property
    def is_visible(self) -> bool:
        return (
            self._page.locator("input[name='login']").is_visible()
            and self._page.locator("input[name='password']").is_visible()
        )
