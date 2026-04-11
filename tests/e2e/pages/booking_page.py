from __future__ import annotations

from playwright.sync_api import Page
from .base_page import BasePage


class BookingSearchPage(BasePage):
    PATH = "/portal/patient/booking/"

    @property
    def is_on_page(self) -> bool:
        return self.PATH in self._page.url


class BookingConfirmPage(BasePage):
    def __init__(self, page: Page, base_url: str, medecin_id: int) -> None:
        super().__init__(page, base_url)
        self._medecin_id = medecin_id
        self.PATH = f"/portal/patient/booking/{medecin_id}/"

    def fill_and_submit(self, date_heure: str, motif: str) -> None:
        """date_heure format: '2027-06-15 10:00:00'"""
        self._page.fill("input[name='date_heure']", date_heure)
        self._page.fill("input[name='motif']", motif)
        self._page.click("button[type='submit']")
