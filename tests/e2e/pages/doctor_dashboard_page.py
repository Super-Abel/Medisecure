from __future__ import annotations

from .base_page import BasePage


class DoctorDashboardPage(BasePage):
    PATH = "/portal/doctor/"

    def finish_consultation(self, patient_name: str) -> None:
        # Find the row with the patient name and click the Terminer button
        # Using a locator that finds the text and then the sibling button in the same row
        row = self._page.locator("tr", has_text=patient_name)
        row.locator("button:has-text('Terminer')").click()

    def is_consultation_finished(self, patient_name: str) -> bool:
        row = self._page.locator("tr", has_text=patient_name)
        return row.locator("span:has-text('Terminé')").is_visible()
