"""Fixtures partagées pour les tests E2E."""

from __future__ import annotations

import os

import pytest

# Playwright exécute les tests dans un event loop async ;
# Django doit autoriser les opérations DB synchrones dans ce contexte.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

from medisecure.medical.models import Specialite
from medisecure.users.models import Medecin, Patient, Roles

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_verified_user(email: str, password: str, **kwargs) -> User:
    user = User.objects.create_user(email=email, password=password, is_active=True, **kwargs)
    EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)
    user._plain_password = password
    return user


# ---------------------------------------------------------------------------
# Fixtures génériques
# ---------------------------------------------------------------------------

@pytest.fixture
def server_url(live_server) -> str:
    return live_server.url


@pytest.fixture
def verified_user(db) -> User:
    return _make_verified_user("e2e_user@test.com", "E2eTestPass123!")


@pytest.fixture
def admin_user(db) -> User:
    password = "AdminPass123!"  # noqa: S105
    user = User.objects.create_superuser(email="admin_e2e@test.com", password=password)
    EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
    user._plain_password = password
    return user


# ---------------------------------------------------------------------------
# Fixtures RDV
# ---------------------------------------------------------------------------

@pytest.fixture
def specialite(db) -> Specialite:
    return Specialite.objects.create(nom_specialite="Médecine générale")


@pytest.fixture
def patient_user(db) -> User:
    user = _make_verified_user("patient_e2e@test.com", "PatientPass123!", role=Roles.PATIENT)
    Patient.objects.create(user=user)
    return user


@pytest.fixture
def doctor_user(db, specialite) -> User:
    user = _make_verified_user("doctor_e2e@test.com", "DoctorPass123!", role=Roles.MEDECIN)
    Medecin.objects.create(user=user, specialite=specialite, numero_licence="E2E-001")
    return user
