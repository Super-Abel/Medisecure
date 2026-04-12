from __future__ import annotations

from .base_page import BasePage


class SignupPage(BasePage):
    PATH = "/accounts/signup/"

    def signup(
        self, email: str, password: str, nom: str, prenom: str, role: str = "PATIENT"
    ) -> None:
        self._page.fill("input[name='email']", email)
        self._page.fill("input[name='password1']", password)
        self._page.fill("input[name='password2']", password)
        # Based on REQUIRED_FIELDS and custom User model
        if self._page.locator("input[name='nom']").count() > 0:
            self._page.fill("input[name='nom']", nom)
        if self._page.locator("input[name='prenom']").count() > 0:
            self._page.fill("input[name='prenom']", prenom)

        # New role field
        if self._page.locator("select[name='role']").count() > 0:
            self._page.select_option("select[name='role']", role)

        self._page.click("button[type='submit']")

    @property
    def is_visible(self) -> bool:
        return self._page.locator("input[name='email']").is_visible()
