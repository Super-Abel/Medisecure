from typing import Optional
from medisecure.domain.models import UserEntity, LogEntity
from medisecure.domain.repositories import UserRepository, LogRepository


class AuthService:
    def __init__(self, user_repo: UserRepository, log_repo: LogRepository):
        self.user_repo = user_repo
        self.log_repo = log_repo

    def login(
        self, email: str, ip_address: Optional[str] = None
    ) -> Optional[UserEntity]:
        user = self.user_repo.get_by_email(email)
        if user and user.statut is True:  # Required verification
            self.log_repo.record(
                LogEntity(
                    id_log=None,
                    utilisateur_id=user.id_utilisateur,
                    action=f"Connexion réussie : {email}",
                    adresse_ip=ip_address,
                )
            )
            return user
        if user and user.statut is False:
            self.log_repo.record(
                LogEntity(
                    id_log=None,
                    utilisateur_id=user.id_utilisateur,
                    action=f"Échec connexion (email non vérifié) : {email}",
                    adresse_ip=ip_address,
                )
            )
        return None

    def logout(self, user_id: int, ip_address: Optional[str] = None) -> None:
        self.log_repo.record(
            LogEntity(
                id_log=None,
                utilisateur_id=user_id,
                action="Déconnexion",
                adresse_ip=ip_address,
            )
        )

    def send_verification_email(self, user_id: int, email: str) -> None:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from medisecure.users.models import User, EmailVerificationToken

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return

        token = EmailVerificationToken.objects.create(utilisateur=user)
        self.log_repo.record(LogEntity(None, user.id, "Envoi email de vérification"))

        html_message = render_to_string(
            "emails/verification_email.html",
            {
                "otp": token.otp,
                "verification_url": f"http://localhost:8000/api/auth/verify-email/?token={token.token}",
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject="MediSecure - Vérifiez votre adresse email",
            message=plain_message,
            html_message=html_message,
            from_email="noreply@medisecure.com",
            recipient_list=[email],
            fail_silently=True,
        )

    def verify_email(self, token: str = None, otp: str = None) -> bool:
        from medisecure.users.models import EmailVerificationToken

        try:
            if token:
                vt = EmailVerificationToken.objects.select_related("utilisateur").get(
                    token=token
                )
            elif otp:
                vt = EmailVerificationToken.objects.select_related("utilisateur").get(
                    otp=otp
                )
            else:
                return False
        except EmailVerificationToken.DoesNotExist:
            return False

        if not vt.is_valid():
            return False

        vt.utilisateur.statut = True
        vt.utilisateur.save()
        vt.used = True
        vt.save()

        self.log_repo.record(
            LogEntity(None, vt.utilisateur.id, "Email vérifié avec succès")
        )
        return True

    def forgot_password(self, email: str) -> Optional[str]:
        """Génère et envoie un token de réinitialisation par email. Retourne le token."""
        from medisecure.users.models import User, PasswordResetToken
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        reset = PasswordResetToken.objects.create(utilisateur=user)
        self.log_repo.record(
            LogEntity(
                id_log=None,
                utilisateur_id=user.id,
                action="Demande réinitialisation mot de passe",
            )
        )

        html_message = render_to_string(
            "emails/forgot_password.html",
            {
                "token": reset.token,
                "reset_url": f"http://localhost:8000/api/auth/reset-password/?token={reset.token}",
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject="MediSecure - Réinitialisation de mot de passe",
            message=plain_message,
            html_message=html_message,
            from_email="noreply@medisecure.com",
            recipient_list=[email],
            fail_silently=True,
        )
        return str(reset.token)

    def reset_password(self, token: str, new_password: str) -> bool:
        """Réinitialise le mot de passe via token. Retourne True si succès."""
        from medisecure.users.models import PasswordResetToken

        try:
            reset = PasswordResetToken.objects.select_related("utilisateur").get(
                token=token
            )
        except (PasswordResetToken.DoesNotExist, Exception):
            return False
        if not reset.is_valid():
            return False
        reset.utilisateur.set_password(new_password)
        reset.utilisateur.save()
        reset.used = True
        reset.save()
        self.log_repo.record(
            LogEntity(
                id_log=None,
                utilisateur_id=reset.utilisateur.id,
                action="Mot de passe réinitialisé",
            )
        )
        return True
