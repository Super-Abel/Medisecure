from __future__ import annotations

from .base_page import BasePage


class DoctorDashboardPage(BasePage):
    PATH = "/portal/doctor/"

    def navigate(self, date: str | None = None) -> None:
        url = f"{self._base_url}{self.PATH}"
        if date:
            url += f"?date={date}"
        self._page.goto(url)

    def finish_consultation(self, patient_name: str) -> None:
        row = self._page.locator("tr").filter(has_text=patient_name).first
        btn = row.get_by_role("button", name="Terminer", exact=True)
        with self._page.expect_navigation():
            btn.click()

    def is_consultation_finished(self, patient_name: str) -> bool:
        try:
            self._page.locator("span.badge.rounded-pill", has_text="Termin").wait_for(
                state="visible", timeout=5000
            )
            return True
        except Exception:
            return False
