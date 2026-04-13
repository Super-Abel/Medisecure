from __future__ import annotations

from .base_page import BasePage


class SignupPage(BasePage):
    PATH = "/accounts/signup/"

    def navigate(self, role: str = "PATIENT") -> None:
        self._page.goto(f"{self._base_url}{self.PATH}?role={role}")

    def signup(
        self, email: str, password: str, nom: str, prenom: str, role: str = "PATIENT"
    ) -> None:
        self._page.fill("input[name='email']", email)
        self._page.fill("input[name='password1']", password)
        self._page.fill("input[name='password2']", password)

        if self._page.locator("input[name='nom']").count() > 0:
            self._page.fill("input[name='nom']", nom)
        if self._page.locator("input[name='prenom']").count() > 0:
            self._page.fill("input[name='prenom']", prenom)

        # In UserSignupForm, role is a HiddenInput.
        # But since we use the query param in navigate, it should be set correctly.
        # However, we can also force it if we find the hidden input.
        role_el = self._page.locator("input[name='role']")
        if role_el.count() > 0:
            role_el.evaluate(f"el => el.value = '{role}'")

        self._page.click("button[type='submit']")

    @property
    def is_visible(self) -> bool:
        return self._page.locator("input[name='email']").is_visible()
