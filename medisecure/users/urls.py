from django.urls import path

from .views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
    medecin_profil_completion_view,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path(
        "medecin/completer-profil/",
        view=medecin_profil_completion_view,
        name="complete-medecin-profil",
    ),
]
