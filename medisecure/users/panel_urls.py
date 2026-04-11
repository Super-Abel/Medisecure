from django.urls import path
from . import panel_views as v

app_name = "admin_panel"

urlpatterns = [
    path("", v.dashboard, name="dashboard"),
    path("users/", v.users, name="users"),
    path("users/create/", v.create_user, name="create_user"),
    path("users/bulk/", v.bulk_action_users, name="bulk_action_users"),
    path("users/<int:user_id>/role/", v.change_role, name="change_role"),
    path(
        "users/<int:user_id>/toggle/", v.toggle_user_status, name="toggle_user_status"
    ),
    path("patients/", v.patients, name="patients"),
    path("patients/bulk/", v.bulk_action_patients, name="bulk_action_patients"),
    path("patients/<int:pk>/edit/", v.edit_patient, name="edit_patient"),
    path("medecins/", v.medecins, name="medecins"),
    path("medecins/<int:pk>/edit/", v.edit_medecin, name="edit_medecin"),
    path("specialites/", v.specialites, name="specialites"),
    path("specialites/create/", v.create_specialite, name="create_specialite"),
    path("specialites/<int:pk>/delete/", v.delete_specialite, name="delete_specialite"),
    path("cabinets/", v.cabinets, name="cabinets"),
    path("cabinets/create/", v.create_cabinet, name="create_cabinet"),
    path("cabinets/<int:pk>/delete/", v.delete_cabinet, name="delete_cabinet"),
    path("rdvs/", v.rdvs, name="rdvs"),
    path("rdvs/bulk/", v.bulk_action_rdvs, name="bulk_action_rdvs"),
    path("rdvs/<int:pk>/cancel/", v.cancel_rdv, name="cancel_rdv"),
    path("logs/", v.logs, name="logs"),
]
