import pytest
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta

from .pages import (
    SignupPage,
    LoginPage,
    ProfilePage,
    PlanningPage,
    BookingConfirmPage,
    DoctorDashboardPage,
    DossierPage,
)


@pytest.mark.django_db
@pytest.mark.e2e
def test_full_consultation_lifecycle(page: Page, live_server):
    # Use live_server.url specifically
    base_url = live_server.url
    page.set_default_timeout(120000)  # 120s
    print(f"DEBUG: Starting test at {base_url}")
    timestamp = int(datetime.now().timestamp())
    patient_email = f"patient_{timestamp}@test.com"
    doctor_email = f"doctor_{timestamp}@test.com"

    # --- 1. PATIENT SIGNUP & PROFILE ---
    signup_patient = SignupPage(page, base_url)
    print(f"DEBUG: Navigating to patient signup")
    try:
        signup_patient.navigate(role="PATIENT")
    except Exception as e:
        print(f"DEBUG: Navigation failed: {e}")
        print(f"DEBUG: Current URL: {page.url}")
        print(f"DEBUG: Page Content Snippet: {page.content()[:500]}")
        raise

    print(f"DEBUG: Current URL: {page.url}")
    signup_patient.signup(
        email=patient_email,
        password="PatientPass123!",
        nom="Dupont",
        prenom="Jean",
        role="PATIENT",
    )

    # Wait for the redirect after signup
    try:
        page.wait_for_url(
            lambda url: "/portal/patient/" in url or "/accounts/login/" in url,
            timeout=20000,
        )
    except Exception:
        print(f"DEBUG: Signup redirect timed out. Current URL: {page.url}")
        print(f"DEBUG: Page Content: {page.content()[:1000]}")
        raise

    if "/accounts/login/" in page.url:
        print("DEBUG: Redirected to login after signup, logging in...")
        login_page = LoginPage(page, base_url)
        login_page.login(patient_email, "PatientPass123!")
        page.wait_for_url("**/portal/patient/**")

    # Update Patient Profile
    profile_page = ProfilePage(page, base_url)
    profile_page.navigate()
    profile_page.open_edit_form()
    profile_page.fill_personal_info(prenom="Jean", nom="Dupont", telephone="0123456789")
    profile_page.fill_patient_info(
        sanguin="O+", poids="75", taille="180", allergies="Pollen"
    )
    profile_page.save()

    # Logout
    page.goto(f"{base_url}/accounts/logout/")
    page.click("button[type='submit']")

    # --- 2. DOCTOR SIGNUP & AVAILABILITY ---
    signup_doctor = SignupPage(page, base_url)
    signup_doctor.navigate(role="MEDECIN")
    signup_doctor.signup(
        email=doctor_email,
        password="DoctorPass123!",
        nom="Martin",
        prenom="Alice",
        role="MEDECIN",
    )

    # Wait for the redirect after signup
    page.wait_for_url(
        lambda url: "/portal/doctor/" in url
        or "/accounts/login/" in url
        or "/portal/profile/" in url,
        timeout=30000,
    )

    if "/accounts/login/" in page.url:
        print("DEBUG: Redirected to login after doctor signup, logging in...")
        login_page = LoginPage(page, base_url)
        login_page.login(doctor_email, "DoctorPass123!")
        page.wait_for_url("**/portal/doctor/**")

    # Update Doctor Profile (RPPS is needed for some views)
    profile_page = ProfilePage(page, base_url)
    profile_page.navigate()
    profile_page.open_edit_form()
    profile_page.fill_medecin_info(rpps="12345678901")
    profile_page.save()

    # Create Availability
    planning_page = PlanningPage(page, base_url)
    planning_page.navigate()

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    planning_page.open_availability_modal()
    planning_page.configure_availability(
        date=tomorrow, start_time="09:00", end_time="12:00"
    )

    # Logout
    page.goto(f"{base_url}/accounts/logout/")
    page.click("button[type='submit']")

    # --- 3. PATIENT BOOKING ---
    login_page = LoginPage(page, base_url)
    login_page.navigate()
    login_page.login(patient_email, "PatientPass123!")

    # Search and Book
    page.goto(f"{base_url}/portal/patient/booking/")
    # Wait for the page to be ready (HTMX load)
    page.wait_for_selector("input[name='q']")
    page.locator("input[name='q']").press_sequentially("Martin", delay=100)

    # Wait for results via HTMX
    page.wait_for_selector("text=Alice Martin")

    # Click the "Choisir" button for the first result (Alice Martin)
    page.get_by_role("link", name="Choisir").first.click()

    # 1. Select Tomorrow
    tomorrow_day = (datetime.now() + timedelta(days=1)).day
    page.locator(".day-card", has_text=str(tomorrow_day)).click()

    # 2. Select first available slot
    page.wait_for_selector(".time-slot")
    page.locator(".time-slot").first.click()

    # 3. Fill motif and confirm
    page.fill("#id_motif", "Consultation de test")
    page.get_by_role("button", name="Confirmer le rendez-vous").click()

    # Verify we are back on patient dashboard
    page.wait_for_url("**/portal/patient/", timeout=15000)
    expect(page).to_have_url(f"{base_url}/portal/patient/")
    expect(page.get_by_text("Dr. Martin Alice")).to_be_visible()

    # Logout
    page.goto(f"{base_url}/accounts/logout/")
    page.click("button[type='submit']")

    # --- 4. DOCTOR CONSULTATION ---
    login_page.navigate()
    login_page.login(doctor_email, "DoctorPass123!")

    # Go to Dashboard (tomorrow's date to see the booked RDV)
    doctor_dash = DoctorDashboardPage(page, base_url)
    doctor_dash.navigate(date=tomorrow)

    # Find patient and open dossier
    row = page.locator("tr").filter(has_text="Jean Dupont").first
    row.get_by_role("link", name="Dossier").click()

    dossier_page = DossierPage(
        page, base_url, patient_id=0
    )  # already navigated via click
    dossier_page.update_dossier(antecedents="Aucun", allergies="Pollen (confirmé)")

    # Back to dashboard and finish
    doctor_dash.navigate(date=tomorrow)
    doctor_dash.finish_consultation("Jean Dupont")

    # Re-navigate to tomorrow's view to verify status changed to Terminé
    doctor_dash.navigate(date=tomorrow)
    assert doctor_dash.is_consultation_finished("Jean Dupont")
