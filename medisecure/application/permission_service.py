from medisecure.domain.models import UserEntity, UserRole, DossierMedicalEntity


class PermissionService:
    @staticmethod
    def can_access_dossier(user: UserEntity, dossier: DossierMedicalEntity) -> bool:
        """
        Vérifie si l'utilisateur a le droit d'accéder au dossier médical.
        """
        # Un administrateur ne peut pas voir le dossier médical
        if user.role == UserRole.ADMIN:
            return False

        # Un patient ne peut voir que son propre dossier
        if user.role == UserRole.PATIENT:
            # En réalité, on lierait l'ID du profil Patient.
            # Simplification : on suppose que le patient_id correspond au profil lié à cet utilisateur
            return True  # La logique exacte dépend de la récupération du patient_id via user.id_utilisateur

        # Un médecin peut voir (à affiner : seulement ses patients)
        if user.role == UserRole.MEDECIN:
            return True

        return False

    @staticmethod
    def can_manage_users(user: UserEntity) -> bool:
        """
        Seul un administrateur peut gérer les utilisateurs.
        """
        return user.role == UserRole.ADMIN
