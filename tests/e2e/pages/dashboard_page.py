from __future__ import annotations

from .base_page import BasePage


class DashboardPage(BasePage):
    PATH = "/dashboard/"

    @property
    def is_on_dashboard(self) -> bool:
        return self.PATH in self._page.url
