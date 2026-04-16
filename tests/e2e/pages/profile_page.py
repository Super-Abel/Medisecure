from __future__ import annotations

from .base_page import BasePage


class ProfilePage(BasePage):
    PATH = "/users/me/"

    def navigate(self) -> None:
        # Click the "Profil" link in the bottom navigation bar or header
        self._page.get_by_role("link", name="Profil").click()
        self._page.wait_for_load_state("networkidle")

    def open_edit_form(self) -> None:
        # The edit panel is toggled by clicking the header
        if not self._page.locator("#editFormCollapse").is_visible():
            self._page.click(".edit-panel-header")
            self._page.wait_for_selector("#editFormCollapse", state="visible")

    def fill_personal_info(self, prenom: str, nom: str, telephone: str) -> None:
        self._page.fill("#inputPrenom", prenom)
        self._page.fill("#inputNom", nom)
        self._page.fill("#inputTelephone", telephone)

    def fill_patient_info(
        self, sanguin: str = "", poids: str = "", taille: str = "", allergies: str = ""
    ) -> None:
        # Sanguin is a select
        if sanguin:
            self._page.select_option("#inputSanguin", sanguin)
        if poids:
            self._page.fill("#inputPoids", str(poids))
        if taille:
            self._page.fill("#inputTaille", str(taille))
        if allergies:
            self._page.fill("#inputAllergies", allergies)

    def fill_medecin_info(
        self, specialite: str = "", cabinet: str = "", rpps: str = ""
    ) -> None:
        if specialite:
            self._page.locator("#inputSpecSelect").select_option(specialite, force=True)
        if cabinet:
            self._page.locator("#inputCabinetSelect").select_option(cabinet, force=True)
        if rpps:
            self._page.locator("#inputRpps").fill(rpps, force=True)

    def save(self) -> None:
        self._page.click("#saveBtn")
        # Wait for success alert or spinner completion
        self._page.wait_for_selector("#successAlert", state="visible", timeout=5000)

    @property
    def is_visible(self) -> bool:
        return self._page.locator("#displayName").is_visible()
