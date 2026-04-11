from __future__ import annotations

from .base_page import BasePage


class DossierPage(BasePage):
    """Page objects for Doctor managing Patient's Medical Record."""

    def __init__(self, page, base_url, patient_id: int) -> None:
        super().__init__(page, base_url)
        self.PATH = f"/portal/doctor/patients/{patient_id}/dossier/"

    def update_dossier(self, antecedents: str, allergies: str) -> None:
        self._page.fill("textarea[name='antecedents']", antecedents)
        self._page.fill("textarea[name='allergies']", allergies)
        self._page.click("button[type='submit']")
