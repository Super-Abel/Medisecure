from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from medisecure.medical.models import Cabinet, Specialite
from medisecure.rdv.models import RendezVous
from .models import LogActivite, Medecin, Patient, User

PER_PAGE_CHOICES = [10, 25, 50, 100]


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.role == "ADMIN")


def admin_view(func):
    return login_required(login_url="/accounts/login/")(
        user_passes_test(is_admin, login_url="/accounts/login/")(func)
    )


def get_per_page(request, default=10):
    try:
        val = int(request.GET.get("per_page", default))
        return val if val in PER_PAGE_CHOICES else default
    except (ValueError, TypeError):
        return default


def record_ad_log(request, action):
    """Helper for audit logs in admin panel."""
    # Get client IP
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    LogActivite.objects.create(
        utilisateur=request.user, action=f"[ADMIN] {action}", adresse_ip=ip
    )


# ── DASHBOARD ──────────────────────────────────────────────────────────────────
@admin_view
def dashboard(request):
    # Stats de base
    stats = {
        "total_users": User.objects.count(),
        "total_patients": Patient.objects.count(),
        "total_medecins": Medecin.objects.count(),
        "total_rdvs": RendezVous.objects.count(),
        "total_logs": LogActivite.objects.count(),
    }

    # Données pour les graphiques
    # 1. Répartition Utilisateurs
    roles_data = [
        User.objects.filter(role="PATIENT").count(),
        User.objects.filter(role="MEDECIN").count(),
        User.objects.filter(role="ADMIN").count(),
    ]

    # 2. Statut des RDV
    rdv_status_labels = ["EN_ATTENTE", "CONFIRME", "ANNULE", "TERMINE"]
    rdv_status_data = [
        RendezVous.objects.filter(statut=s).count() for s in rdv_status_labels
    ]

    return render(
        request,
        "admin_panel/dashboard.html",
        {
            "stats": stats,
            "recent_logs": LogActivite.objects.select_related("utilisateur").order_by(
                "-date_action"
            )[:10],
            "pending_rdvs": RendezVous.objects.select_related(
                "patient__user", "medecin__user"
            )
            .filter(statut="EN_ATTENTE")
            .order_by("date_heure")[:8],
            "chart_data": {
                "roles": roles_data,
                "rdv_status": rdv_status_data,
            },
        },
    )


# ── USERS ──────────────────────────────────────────────────────────────────────
@admin_view
def users(request):
    qs = User.objects.order_by("-date_joined")
    q = request.GET.get("q", "")
    role = request.GET.get("role", "")
    statut = request.GET.get("statut", "")
    if q:
        qs = qs.filter(
            Q(email__icontains=q) | Q(nom__icontains=q) | Q(prenom__icontains=q)
        )
    if role:
        qs = qs.filter(role=role)
    if statut != "":
        qs = qs.filter(statut=bool(int(statut)))
    per_page = get_per_page(request)
    paginator = Paginator(qs, per_page)
    return render(
        request,
        "admin_panel/users.html",
        {
            "page_obj": paginator.get_page(request.GET.get("page")),
            "per_page": per_page,
            "per_page_choices": PER_PAGE_CHOICES,
        },
    )


@admin_view
def change_role(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        role = request.POST.get("role")
        if role in ("PATIENT", "MEDECIN", "ADMIN"):
            old_role = user.role
            user.role = role
            user.save()
            msg = f"Rôle de {user.email} changé : {old_role} → {role}"
            record_ad_log(request, msg)
            messages.success(request, f"Rôle de {user.email} → {role}")
        else:
            messages.error(request, "Rôle invalide.")
    return redirect("admin_panel:users")


@admin_view
def toggle_user_status(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.statut = not user.statut
        user.save()
        action_str = "activé" if user.statut else "désactivé"
        record_ad_log(request, f"Utilisateur {user.email} {action_str}")
        messages.success(request, f"{user.email} {action_str}.")
    return redirect(request.META.get("HTTP_REFERER", "admin_panel:users"))


@admin_view
def create_user(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email {email} déjà utilisé.")
        else:
            User.objects.create_user(
                email=email,
                password=request.POST.get("password", ""),
                nom=request.POST.get("nom", "").strip(),
                prenom=request.POST.get("prenom", "").strip(),
                role=request.POST.get("role", "PATIENT"),
                statut=True,
            )
            record_ad_log(
                request,
                f"Création utilisateur : {email} (Rôle: {request.POST.get('role')})",
            )
            messages.success(request, f"Utilisateur {email} créé.")
    return redirect("admin_panel:users")


@admin_view
def bulk_action_users(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        action = request.POST.get("action", "")
        if not ids:
            messages.error(request, "Aucun utilisateur sélectionné.")
            return redirect("admin_panel:users")
        qs = User.objects.filter(id__in=ids)
        if action == "activate":
            qs.update(statut=True)
            record_ad_log(
                request, f"Action groupée : Activation de {qs.count()} utilisateur(s)"
            )
            messages.success(request, f"{qs.count()} utilisateur(s) activé(s).")
        elif action == "deactivate":
            qs.update(statut=False)
            record_ad_log(
                request,
                f"Action groupée : Désactivation de {qs.count()} utilisateur(s)",
            )
            messages.success(request, f"{qs.count()} utilisateur(s) désactivé(s).")
        elif action in ("role_patient", "role_medecin", "role_admin"):
            role = action.split("_")[1].upper()
            qs.update(role=role)
            record_ad_log(
                request,
                f"Action groupée : Rôle → {role} pour {qs.count()} utilisateur(s)",
            )
            messages.success(
                request, f"Rôle → {role} appliqué à {qs.count()} utilisateur(s)."
            )
        else:
            messages.error(request, "Action invalide.")
    return redirect("admin_panel:users")


# ── PATIENTS ───────────────────────────────────────────────────────────────────
@admin_view
def patients(request):
    qs = (
        Patient.objects.select_related("user")
        .prefetch_related("dossier")
        .order_by("-user__date_joined")
    )
    q = request.GET.get("q", "")
    if q:
        qs = qs.filter(
            Q(user__email__icontains=q)
            | Q(user__nom__icontains=q)
            | Q(user__prenom__icontains=q)
        )
    per_page = get_per_page(request)
    paginator = Paginator(qs, per_page)
    return render(
        request,
        "admin_panel/patients.html",
        {
            "page_obj": paginator.get_page(request.GET.get("page")),
            "per_page": per_page,
            "per_page_choices": PER_PAGE_CHOICES,
        },
    )


@admin_view
def bulk_action_patients(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        action = request.POST.get("action", "")
        if not ids:
            messages.error(request, "Aucun patient sélectionné.")
            return redirect("admin_panel:patients")
        qs = User.objects.filter(patient_profile__id__in=ids)
        if action == "activate":
            qs.update(statut=True)
            messages.success(request, f"{len(ids)} patient(s) activé(s).")
        elif action == "deactivate":
            qs.update(statut=False)
            messages.success(request, f"{len(ids)} patient(s) désactivé(s).")
        else:
            messages.error(request, "Action invalide.")
    return redirect("admin_panel:patients")


@admin_view
def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        # User fields
        patient.user.nom = request.POST.get("nom", "").strip()
        patient.user.prenom = request.POST.get("prenom", "").strip()
        patient.user.save()
        # Patient fields
        patient.date_naissance = request.POST.get("date_naissance") or None
        patient.sexe = request.POST.get("sexe", "")
        patient.adresse = request.POST.get("adresse", "").strip()
        patient.save()

        record_ad_log(request, f"Édition profil patient : {patient.user.email}")
        messages.success(request, f"Profil de {patient.user.nom} mis à jour.")
    return redirect("admin_panel:patients")


# ── MÉDECINS ───────────────────────────────────────────────────────────────────
@admin_view
def medecins(request):
    qs = Medecin.objects.select_related("user", "specialite", "cabinet").order_by(
        "user__nom"
    )
    return render(
        request,
        "admin_panel/medecins.html",
        {
            "medecins": qs,
            "specialites": Specialite.objects.all(),
            "cabinets": Cabinet.objects.all(),
        },
    )


@admin_view
def edit_medecin(request, pk):
    medecin = get_object_or_404(Medecin, pk=pk)
    if request.method == "POST":
        # User fields
        medecin.user.nom = request.POST.get("nom", "").strip()
        medecin.user.prenom = request.POST.get("prenom", "").strip()
        medecin.user.save()
        # Medecin fields
        medecin.numero_licence = request.POST.get("numero_licence", "").strip()
        spec_id = request.POST.get("specialite")
        cab_id = request.POST.get("cabinet")
        medecin.specialite = (
            Specialite.objects.filter(id=spec_id).first() if spec_id else None
        )
        medecin.cabinet = Cabinet.objects.filter(id=cab_id).first() if cab_id else None
        medecin.save()

        record_ad_log(request, f"Édition profil médecin : {medecin.user.email}")
        messages.success(request, f"Profil de Dr {medecin.user.nom} mis à jour.")
    return redirect("admin_panel:medecins")


# ── SPÉCIALITÉS ────────────────────────────────────────────────────────────────
@admin_view
def specialites(request):
    return render(
        request,
        "admin_panel/specialites.html",
        {
            "specialites": Specialite.objects.prefetch_related("medecins").order_by(
                "nom_specialite"
            )
        },
    )


@admin_view
def create_specialite(request):
    if request.method == "POST":
        nom = request.POST.get("nom_specialite", "").strip()
        if nom:
            Specialite.objects.create(
                nom_specialite=nom,
                description=request.POST.get("description", "").strip(),
            )
            record_ad_log(request, f"Création spécialité : {nom}")
            messages.success(request, f"Spécialité « {nom} » créée.")
        else:
            messages.error(request, "Nom requis.")
    return redirect("admin_panel:specialites")


@admin_view
def delete_specialite(request, pk):
    if request.method == "POST":
        spec = get_object_or_404(Specialite, pk=pk)
        nom = spec.nom_specialite
        spec.delete()
        record_ad_log(request, f"Suppression spécialité : {nom}")
        messages.success(request, f"Spécialité « {nom} » supprimée.")
    return redirect("admin_panel:specialites")


# ── CABINETS ───────────────────────────────────────────────────────────────────
@admin_view
def cabinets(request):
    return render(
        request,
        "admin_panel/cabinets.html",
        {"cabinets": Cabinet.objects.prefetch_related("medecins").order_by("nom")},
    )


@admin_view
def create_cabinet(request):
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        if nom:
            Cabinet.objects.create(
                nom=nom,
                adresse=request.POST.get("adresse", "").strip(),
                telephone=request.POST.get("telephone", "").strip(),
            )
            record_ad_log(request, f"Création cabinet : {nom}")
            messages.success(request, f"Cabinet « {nom} » créé.")
        else:
            messages.error(request, "Nom requis.")
    return redirect("admin_panel:cabinets")


@admin_view
def delete_cabinet(request, pk):
    if request.method == "POST":
        cabinet = get_object_or_404(Cabinet, pk=pk)
        nom = cabinet.nom
        cabinet.delete()
        record_ad_log(request, f"Suppression cabinet : {nom}")
        messages.success(request, f"Cabinet « {nom} » supprimé.")
    return redirect("admin_panel:cabinets")


# ── RENDEZ-VOUS ────────────────────────────────────────────────────────────────
@admin_view
def rdvs(request):
    qs = RendezVous.objects.select_related(
        "patient__user", "medecin__user", "medecin__specialite"
    ).order_by("-date_heure")
    statut = request.GET.get("statut", "")
    if statut:
        qs = qs.filter(statut=statut)
    per_page = get_per_page(request)
    paginator = Paginator(qs, per_page)
    return render(
        request,
        "admin_panel/rdvs.html",
        {
            "page_obj": paginator.get_page(request.GET.get("page")),
            "per_page": per_page,
            "per_page_choices": PER_PAGE_CHOICES,
        },
    )


@admin_view
def cancel_rdv(request, pk):
    if request.method == "POST":
        rdv = get_object_or_404(RendezVous, pk=pk)
        rdv.statut = "ANNULE"
        rdv.save()
        record_ad_log(
            request, f"Annulation du RDV #{rdv.id} (Patient: {rdv.patient.user.email})"
        )
        messages.success(request, f"RDV #{rdv.id} annulé.")
    return redirect("admin_panel:rdvs")


@admin_view
def bulk_action_rdvs(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        action = request.POST.get("action", "")
        if not ids:
            messages.error(request, "Aucun RDV sélectionné.")
            return redirect("admin_panel:rdvs")
        qs = RendezVous.objects.filter(id__in=ids)
        mapping = {"cancel": "ANNULE", "confirm": "CONFIRME", "termine": "TERMINE"}
        if action in mapping:
            qs.update(statut=mapping[action])
            record_ad_log(request, f"Action groupée RDV : {action} sur {len(ids)} RDV")
            messages.success(request, f"{len(ids)} RDV mis à jour → {mapping[action]}.")
        else:
            messages.error(request, "Action invalide.")
    return redirect("admin_panel:rdvs")


# ── LOGS ───────────────────────────────────────────────────────────────────────
@admin_view
def logs(request):
    qs = LogActivite.objects.select_related("utilisateur").order_by("-date_action")
    q = request.GET.get("q", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    if q:
        qs = qs.filter(Q(action__icontains=q) | Q(utilisateur__email__icontains=q))
    if date_from:
        qs = qs.filter(date_action__date__gte=date_from)
    if date_to:
        qs = qs.filter(date_action__date__lte=date_to)
    per_page = get_per_page(request, default=50)
    paginator = Paginator(qs, per_page)
    return render(
        request,
        "admin_panel/logs.html",
        {
            "page_obj": paginator.get_page(request.GET.get("page")),
            "per_page": per_page,
            "per_page_choices": PER_PAGE_CHOICES,
        },
    )
