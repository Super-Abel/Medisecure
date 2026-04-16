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

    def fill_and_submit(self, date_heure: str, motif: str) -> str:
        """Logic for interactive slots (ignores date_heure for now and picks first avail)"""
        # 1. Select second day (tomorrow) to avoid current time filtering if today is picked
        self._page.locator(".day-card").nth(1).click()

        # 2. Wait for slots to load and select first slot
        slot_locator = self._page.locator(".time-slot").first
        slot_locator.wait_for(state="visible", timeout=30000)
        slot_locator.click()

        # 3. Wait for the hidden input to be updated by JS
        hidden_input = self._page.locator("input[id='id_date_heure']")

        # Poll for value update
        import time

        for _ in range(10):
            val = hidden_input.input_value()
            if val:
                break
            time.sleep(0.5)

        selected_date = val.split("T")[0] if "T" in val else ""

        # 3. Fill motif
        self._page.fill("input[id='id_motif']", motif)
        # 4. Submit
        self._page.click("button[type='submit']")

        return selected_date
