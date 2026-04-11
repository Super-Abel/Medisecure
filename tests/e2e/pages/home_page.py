from __future__ import annotations

from .base_page import BasePage


class HomePage(BasePage):
    PATH = "/"

    @property
    def status(self) -> int | None:
        response = self._page.goto(f"{self._base_url}{self.PATH}")
        return response.status if response else None
