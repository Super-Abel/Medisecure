from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rest_framework.test import APIRequestFactory

from medisecure.users.api.views import UserViewSet

if TYPE_CHECKING:
    from medisecure.users.models import User


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test_me(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)  # type: ignore[call-arg, arg-type, misc]

        response_data = response.data.copy()
        response_date_joined = response_data.pop("date_joined")
        assert response_date_joined is not None

        assert response_data == {
            "id": user.id,
            "url": f"http://testserver/api/users/{user.pk}/",
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "telephone": user.telephone,
            "role": user.role,
            "statut": user.statut,
            "failed_attempts": user.failed_attempts,
            "locked_until": user.locked_until,
            "last_login": user.last_login,
            "patient_profile": None,
            "medecin_profile": None,
        }
