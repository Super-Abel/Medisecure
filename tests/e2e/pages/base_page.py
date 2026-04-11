from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    """Base class for all Page Objects."""

    PATH = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url

    def navigate(self) -> None:
        self._page.goto(f"{self._base_url}{self.PATH}")

    @property
    def current_url(self) -> str:
        return self._page.url

    @property
    def title(self) -> str:
        return self._page.title()

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        self._page.wait_for_load_state(state)

    @property
    def has_error(self) -> bool:
        """Check for common Django/Bootstrap error indicators."""
        return (
            self._page.locator(
                ".errorlist, [class*='alert-danger'], [class*='error'], .invalid-feedback"
            ).count()
            > 0
        )
