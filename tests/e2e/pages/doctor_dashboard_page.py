from __future__ import annotations

from .base_page import BasePage


class DoctorDashboardPage(BasePage):
    PATH = "/portal/doctor/"

    def finish_consultation(self, patient_name: str) -> None:
        # Find the row with the patient name and click the Terminer button
        # Using a locator that finds the text and then the sibling button in the same row
        # Use get_by_role with exact=True to avoid matching other text containing 'Terminer'
        self._page.get_by_role("button", name="Terminer", exact=True).first.click()

    def is_consultation_finished(self, patient_name: str) -> bool:
        row = self._page.locator("tr").filter(has_text=patient_name).first
        badge = row.locator("span:has-text('Terminé')")
        try:
            badge.wait_for(state="visible", timeout=5000)  # Wait for state change
            return True
        except:
            return False
