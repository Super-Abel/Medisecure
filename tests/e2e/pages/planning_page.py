from __future__ import annotations

from .base_page import BasePage


class PlanningPage(BasePage):
    PATH = "/portal/doctor/planning/"

    def open_availability_modal(self) -> None:
        # Click the "⚙️ Horaires" button
        self._page.click("button:has-text('Horaires')")
        self._page.wait_for_selector("#configModal", state="visible")

    def configure_availability(self, date: str, start_time: str, end_time: str) -> None:
        """
        Configure availability for a specific date.
        date format: YYYY-MM-DD
        start_time/end_time format: HH:MM
        """
        self._page.fill("#availDate", date)
        self._page.fill("#availStart", start_time)
        self._page.fill("#availEnd", end_time)
        self._page.click("#btnSaveAvail")

        # Wait for modal to close or alert to appear
        # The script uses alert() which might be tricky in Playwright without a handler,
        # but the modal also hides.
        self._page.wait_for_selector("#configModal", state="hidden", timeout=10000)

    def get_rdv_count(self) -> int:
        return self._page.locator(".appt-slot").count()

    @property
    def is_visible(self) -> bool:
        return self._page.locator("#rdvList").is_visible()
