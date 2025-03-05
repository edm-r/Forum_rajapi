# Documentation du Microservice de Forum

## Présentation du Projet

Ce projet utilisant Django REST Framework implémente un microservice de forum avec authentification et contrôle d'accès basé sur les rôles. Le service permet aux utilisateurs de créer, gérer et interagir avec des forums et des messages.

## Fonctionnalités Principales

- Authentification utilisateur via un token de microservice
- Création et gestion de forums
- Gestion des membres de forum
- Messagerie au sein des forums
- Contrôle d'accès basé sur les rôles (membre, modérateur)

## Authentification

Le projet utilise une `MicroserviceTokenAuthentication` personnalisée qui :
- Valide les tokens via un service d'authentification externe
- Crée automatiquement des utilisateurs s'ils n'existent pas
- Nécessite un token Bearer dans l'en-tête Authorization generer par le service d'authentification (https://rajapi-cop-auth-api.onrender.com/auth)

## Points de Terminaison (Endpoints)

### 1. Forums

#### Créer un Forum
- **Endpoint** : `POST /forums/`
- **Permissions** : Utilisateurs authentifiés
- **Comportement** : 
  - Crée un nouveau forum
  - Ajoute automatiquement le créateur comme modérateur
- **Exemple de Requête** :
```http
POST /forums/
Authorization: Bearer {votre_token}
Content-Type: application/json

{
    "title": "Communauté des Développeurs Python",
    "description": "Un forum pour les passionnés de Python",
    "category": "Programmation"
}
```
- **Exemple de Réponse** :
```json
{
    "id": 1,
    "title": "Communauté des Développeurs Python",
    "description": "Un forum pour les passionnés de Python",
    "category": "Programmation",
    "status": "active",
    "created_at": "2024-03-05T10:30:00Z"
}
```

#### Lister/Récupérer des Forums
- **Endpoint** : `GET /forums/` ou `GET /forums/{forum_id}/`
- **Permissions** : Utilisateurs authentifiés
- **Exemple de Requête** :
```http
GET /forums/1/
Authorization: Bearer {votre_token}
```
- **Exemple de Réponse** :
```json
{
    "id": 1,
    "title": "Communauté des Développeurs Python",
    "description": "Un forum pour les passionnés de Python",
    "category": "Programmation",
    "status": "active",
    "members": [
        {
            "id": 1,
            "email": "createur@exemple.com",
            "username": "maitre_python",
            "role": "moderator",
            "status": "active"
        }
    ],
    "active_members_count": 1
}
```

### 2. Membres du Forum

#### Ajouter un Membre au Forum
- **Endpoint** : `POST /forums/{forum_id}/members/`
- **Permissions** : Propriétaire/modérateur du forum
- **Exemple de Requête** :
```http
POST /forums/1/members/
Authorization: Bearer {votre_token}
Content-Type: application/json

{
    "email": "nouveaumembre@exemple.com"
}
```
- **Exemple de Réponse** :
```json
{
    "id": 2,
    "email": "nouveaumembre@exemple.com",
    "username": "nouvel_utilisateur",
    "role": "member",
    "status": "active",
    "joined_at": "2024-03-05T11:00:00Z"
}
```

#### Supprimer/Désactiver un Membre
- **Endpoint** : `DELETE /forums/{forum_id}/members/{member_id}/`
- **Permissions** : Propriétaire/modérateur du forum
- **Comportement** : Définit le statut du membre sur 'inactif'
- **Exemple de Requête** :
```http
DELETE /forums/1/members/2/
Authorization: Bearer {votre_token}
```
- **Réponse** : 204 Pas de Contenu

### 3. Messages

#### Envoyer un Message
- **Endpoint** : `POST /forums/{forum_id}/messages/`
- **Permissions** : Membres actifs du forum
- **Exemple de Requête** :
```http
POST /forums/1/messages/
Authorization: Bearer {votre_token}
Content-Type: application/json

{
    "content": "Bonjour, communauté Python !"
}
```
- **Exemple de Réponse** :
```json
{
    "id": 1,
    "content": "Bonjour, communauté Python !",
    "author_username": "maitre_python",
    "created_at": "2024-03-05T11:15:00Z",
    "is_edited": false
}
```

#### Modifier un Message
- **Endpoint** : `PATCH /forums/{forum_id}/messages/{message_id}/`
- **Permissions** : Auteur du message uniquement
- **Exemple de Requête** :
```http
PATCH /forums/1/messages/1/
Authorization: Bearer {votre_token}
Content-Type: application/json

{
    "content": "Bonjour, communauté Python ! Message modifié."
}
```
- **Exemple de Réponse** :
```json
{
    "id": 1,
    "content": "Bonjour, communauté Python ! Message modifié.",
    "author_username": "maitre_python",
    "created_at": "2024-03-05T11:15:00Z",
    "updated_at": "2024-03-05T11:20:00Z",
    "is_edited": true
}
```