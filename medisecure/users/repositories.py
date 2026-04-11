from typing import Optional
from medisecure.domain.models import UserEntity, UserRole, LogEntity
from medisecure.domain.repositories import UserRepository, LogRepository
from .models import User, LogActivite


class DjangoUserRepository(UserRepository):
    def get_by_email(self, email: str) -> Optional[UserEntity]:
        try:
            user = User.objects.get(email=email)
            return self._to_entity(user)
        except User.DoesNotExist:
            return None

    def save(self, user_entity: UserEntity) -> UserEntity:
        # Simplifié pour Phase 1
        user, created = User.objects.update_or_create(
            email=user_entity.email,
            defaults={
                "nom": user_entity.nom,
                "prenom": user_entity.prenom,
                "role": user_entity.role.value,
                "telephone": user_entity.telephone,
                "statut": user_entity.statut,
            },
        )
        return self._to_entity(user)

    def _to_entity(self, user: User) -> UserEntity:
        return UserEntity(
            id_utilisateur=user.id,
            nom=user.nom,
            prenom=user.prenom,
            email=user.email,
            role=UserRole(user.role),
            telephone=user.telephone,
            statut=user.statut,
            date_creation=user.date_joined,
        )


class DjangoLogRepository(LogRepository):
    def record(self, log_entity: LogEntity) -> None:
        LogActivite.objects.create(
            utilisateur_id=log_entity.utilisateur_id,
            action=log_entity.action,
            adresse_ip=log_entity.adresse_ip,
        )
