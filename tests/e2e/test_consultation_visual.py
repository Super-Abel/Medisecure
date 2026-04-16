"""
Test E2E visuel : lifecycle complet d'une consultation
- Enregistrement video headless (rapide)
- Captures d'ecran a chaque etape cle
"""
import pytest
from playwright.sync_api import Browser, expect
from datetime import datetime, timedelta
from pathlib import Path

from .pages import SignupPage, ProfilePage, PlanningPage, DoctorDashboardPage, DossierPage


ARTIFACTS_DIR = Path("test-artifacts/consultation-lifecycle")


@pytest.fixture(scope="function")
def visual_context(browser: Browser):
    """Contexte headless avec video + screenshots."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ctx = browser.new_context(
        record_video_dir=str(ARTIFACTS_DIR),
        record_video_size={"width": 1280, "height": 720},
        viewport={"width": 1280, "height": 720},
    )
    yield ctx
    ctx.close()  # flush video sur disque


@pytest.fixture
def vpage(visual_context):
    page = visual_context.new_page()
    page.set_default_timeout(60000)
    yield page
    page.close()


def shot(page, name: str) -> None:
    path = ARTIFACTS_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"  [screenshot] {path}")


def do_signup(page, base: str, email: str, password: str, nom: str, prenom: str, role: str) -> None:
    sp = SignupPage(page, base)
    sp.navigate(role=role)
    sp.signup(email=email, password=password, nom=nom, prenom=prenom, role=role)


def logout(page, base: str, screenshot_name: str = "") -> None:
    page.goto(f"{base}/accounts/logout/")
    if screenshot_name:
        shot(page, screenshot_name)
    page.click("button[type='submit']")


def login(page, base: str, email: str, password: str) -> None:
    page.goto(f"{base}/accounts/login/")
    page.fill("input[name='login']", email)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")


@pytest.mark.django_db(transaction=True)
@pytest.mark.e2e
def test_consultation_visual_lifecycle(vpage, live_server):
    base = live_server.url
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_day = (datetime.now() + timedelta(days=1)).day

    # ── 1. PATIENT SIGNUP ────────────────────────────────────────────────────
    do_signup(vpage, base, "visual_patient@test.com", "PatientPass123!", "Dupont", "Jean", "PATIENT")
    shot(vpage, "01_patient_after_signup")

    # ── 2. PATIENT PROFILE ───────────────────────────────────────────────────
    profile = ProfilePage(vpage, base)
    profile.navigate()
    shot(vpage, "02_patient_profile_page")
    profile.open_edit_form()
    profile.fill_personal_info(prenom="Jean", nom="Dupont", telephone="0123456789")
    profile.fill_patient_info(sanguin="O+", poids="75", taille="180", allergies="Pollen")
    profile.save()
    shot(vpage, "03_patient_profile_saved")

    logout(vpage, base, screenshot_name="03b_logout_page")

    # ── 3. DOCTOR SIGNUP ─────────────────────────────────────────────────────
    do_signup(vpage, base, "visual_doctor@test.com", "DoctorPass123!", "Martin", "Alice", "MEDECIN")
    shot(vpage, "04_doctor_after_signup")

    # ── 4. DOCTOR PROFILE (RPPS) ─────────────────────────────────────────────
    profile = ProfilePage(vpage, base)
    profile.navigate()
    profile.open_edit_form()
    # Attendre que le JS charge les données (async API call)
    vpage.wait_for_load_state("networkidle")
    profile.fill_medecin_info(rpps="12345678901")
    profile.save()
    shot(vpage, "05_doctor_profile_rpps_saved")

    # ── 5. PLANNING : CRER DISPONIBILITE ─────────────────────────────────────
    planning = PlanningPage(vpage, base)
    planning.navigate()
    shot(vpage, "06_doctor_planning_page")

    planning.open_availability_modal()
    shot(vpage, "07_planning_modal_open")

    # Accepter le dialog alert Playwright avant saveAvail
    vpage.on("dialog", lambda d: d.accept())
    planning.configure_availability(date=tomorrow, start_time="09:00", end_time="12:00")
    shot(vpage, "08_planning_saved")

    logout(vpage, base)

    # ── 6. PATIENT LOGIN + BOOKING ───────────────────────────────────────────
    login(vpage, base, "visual_patient@test.com", "PatientPass123!")
    shot(vpage, "09_patient_dashboard")

    vpage.goto(f"{base}/portal/patient/booking/")
    vpage.wait_for_selector("input[name='q']")
    shot(vpage, "10_booking_search_page")

    vpage.locator("input[name='q']").press_sequentially("Martin", delay=100)
    vpage.wait_for_selector("text=Alice Martin")
    shot(vpage, "11_booking_search_results")

    vpage.get_by_role("link", name="Choisir").first.click()
    vpage.locator(".day-card", has_text=str(tomorrow_day)).click()
    shot(vpage, "12_booking_day_selected")

    vpage.wait_for_selector(".time-slot >> text=09:00")
    vpage.locator(".time-slot", has_text="09:00").click()
    shot(vpage, "13_booking_slot_selected")

    vpage.fill("#id_motif", "Consultation de test visuel")
    shot(vpage, "14_booking_motif_filled")

    vpage.get_by_role("button", name="Confirmer le rendez-vous").click()
    expect(vpage).to_have_url(f"{base}/portal/patient/")
    expect(vpage.get_by_text("Dr. Martin Alice")).to_be_visible()
    shot(vpage, "15_patient_dashboard_rdv_confirmed")

    logout(vpage, base)

    # ── 7. DOCTOR : DOSSIER + TERMINER ───────────────────────────────────────
    login(vpage, base, "visual_doctor@test.com", "DoctorPass123!")

    dash = DoctorDashboardPage(vpage, base)
    dash.navigate(date=tomorrow)
    shot(vpage, "16_doctor_dashboard_tomorrow")

    row = vpage.locator("tr").filter(has_text="Jean Dupont").first
    row.get_by_role("link", name="Dossier").click()
    shot(vpage, "17_dossier_form")

    dossier = DossierPage(vpage, base, patient_id=0)
    dossier.update_dossier(antecedents="Aucun", allergies="Pollen (confirme)")
    shot(vpage, "18_after_dossier_save")

    dash.navigate(date=tomorrow)
    shot(vpage, "19_doctor_dashboard_before_finish")

    dash.finish_consultation("Jean Dupont")
    shot(vpage, "20_after_finish_click_redirect")

    # Re-navigate pour verifier le badge Termine (attendre la fin du redirect d'abord)
    vpage.wait_for_load_state("networkidle")
    dash.navigate(date=tomorrow)
    vpage.wait_for_load_state("networkidle")
    shot(vpage, "21_doctor_dashboard_after_finish")

    # Verifier le badge Terminé dans le DOM
    termine_badge = vpage.locator("span.badge.rounded-pill", has_text="Termin")
    termine_badge.wait_for(state="visible", timeout=5000)
    shot(vpage, "22_consultation_terminee_badge")

    assert dash.is_consultation_finished("Jean Dupont")
    print(f"\n[OK] Artifacts saved in: {ARTIFACTS_DIR.resolve()}")
