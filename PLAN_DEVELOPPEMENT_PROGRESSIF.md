# Plan de Développement Progressif : MediSecure 🏥

Ce document définit les étapes de développement de la plateforme MediSecure, en se basant sur l'analyse technique et les exigences de cybersécurité établies dans la documentation.

L'ensemble du projet suivra une **Architecture Clean** pour garantir la testabilité, la maintenabilité et l'indépendance vis-à-vis des frameworks.

---

## 🏛️ Principes de l'Architecture Clean

Afin de respecter la "Clean Architecture", nous séparerons le code en trois couches indépendantes :

1. **Couche Domaine (Domain) :** Contient les entités métier pures et les règles fondamentales (ex: logique de validation d'un diagnostic). Indépendante de Django.
2. **Couche Application (Use Cases) :** Orchestre les flux de données et implémente les cas d'utilisation (ex: "Prendre un rendez-vous", "Chiffrer un dossier médical").
3. **Couche Infrastructure (Adapters) :** Contient les implémentations liées au framework (Modèles Django, Vues API, Tâches Celery, Persistance SQL).

---

## 🏗️ Phase 1 : Infrastructure & Sécurité (Authentification)

**Objectif :** Mettre en place la base solide et sécurisée du projet.

1.  **Modèles & Entités (Domaine & Infra) :**
    - Définir les entités métier `Utilisateur`, `Patient`, `Medecin`.
    - Implémenter les modèles Django correspondants dans la couche Infrastructure.
    - Configurer la validation stricte des emails et des mots de passe.
2.  **Cas d'Utilisation : Authentification :**
    - Implémenter les services de Login/Signup dans la couche Application.
    - Gestion des sessions et déconnexion automatique (contrainte sécurité).
3.  **Logs d'activité (Audit) :**
    - Implémenter la table `log_activite` pour enregistrer chaque connexion et action sensible (Audit Trail).

---

## 📅 Phase 2 : Gestion Médicale de Base

**Objectif :** Organiser le référentiel des soins.

1.  **Etablissements (Cabinets) :**
    - CRUD pour la table `cabinet`.
2.  **Spécialités :**
    - Gestion des spécialités médicales (`specialite`).
3.  **Annuaire interne :**
    - Attribution des médecins aux cabinets et aux spécialités.
    - Vue liste des médecins pour les patients.

---

## 🤝 Phase 3 : Module de Rendez-vous

**Objectif :** Implémenter le cœur fonctionnel (US 2.1).

1.  **Prise de RDV par le Patient :**
    - Sélection du motif, de la spécialité et du médecin.
    - Validation des disponibilités.
2.  **Gestion du Planning (Médecin) :**
    - Vue calendrier des rendez-vous.
    - Changement de statut (Confirmé, Annulé).
3.  **Historique :**
    - Interface permettant au patient de voir ses RDV passés et futurs.

---

## 🔒 Phase 4 : Dossier Médical & Chiffrement

**Objectif :** Gérer les données de santé avec une sécurité maximale.

1.  **Dossier Médical :**
    - Création du modèle `dossier_medical` lié au patient.
2.  **Sécurisation des données (AES-256) :**
    - Mise en place du chiffrement pour les champs sensibles (Antécédents, Traitements, Allergies).
3.  **Contrôle d'accès (RBAC) :**
    - Seuls le médecin traitant et le patient propriétaire peuvent accéder au dossier.

---

## 🔔 Phase 5 : Notifications & Finitions

**Objectif :** Améliorer l'expérience utilisateur et automatiser les rappels.

1.  **Système de Notifications :**
    - Enregistrement des notifications en base.
    - Tâches Celery pour l'envoi de rappels automatiques avant les RDV.
2.  **Dashboard Administrateur :**
    - Vue globale pour l'admin (gestion utilisateurs, consultation des logs).
3.  **Tests Finaux :**
    - Vérification de la conformité avec le cahier des charges cybersécurité.

---

## 🚀 Comment Commencer ?

Pour chaque phase, vous pouvez me demander :
- *"Donne-moi le code pour l'étape 1 de la Phase 1"*
- *"Génère les modèles Django pour le Dossier Médical de la Phase 4"*

Le projet respectera scrupuleusement le [Schéma SQL](file:///d:/Python/Medisecure/Docs%20MediSecure/Schema.sql) déjà établi.
