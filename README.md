# 🛍️ Paruise Shop Data Manager

> **Statut :**  En Production (v1.0)
> **Stack :** Python | Streamlit | Google Sheets API
> **Impact :** Digitalisation complète d'une boutique physique

##  Le Contexte Business
**Paruise Shop** est une boutique de prêt-à-porter située à Wonyomé. Jusqu'à récemment, la gestion (stocks, ventes, comptabilité) était effectuée manuellement, entraînant des erreurs de stock et un manque de visibilité financière.

Ce projet est un **ERP sur-mesure** développé pour digitaliser l'activité sans infrastructure coûteuse.

## La Solution
Une Web App interactive qui sert de terminal de gestion pour le personnel.

### Fonctionnalités Clés :
1.  **Caisse Digitale (POS) :** Enregistrement des ventes en 3 clics et génération de reçus WhatsApp automatiques.
2.  **Gestion de Stock en Temps Réel :** Mise à jour automatique et alertes de rupture de stock.
3.  **CRM Intégré :** Suivi des clientes et générateur de messages de fidélisation (IA/Templates).
4.  **Pilotage Financier :** Dashboard automatique du Chiffre d'Affaires et des dépenses.

## Architecture Technique

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Frontend** | **Streamlit** | Interface utilisateur responsive (Mobile/Desktop). |
| **Database** | **Google Sheets API** | Base de données NoSQL légère et gratuite. |
| **Analytics** | **Pandas & Plotly** | Traitement des données et visualisation graphique. |
| **DevOps** | **Docker** | Environnement de développement conteneurisé. |

##  Aperçu du Code
Connexion sécurisée à l'API Google via `st.secrets` (Secrets Management) :

```python
# Exemple de connexion sécurisée
def get_database():
    scope = ['[https://www.googleapis.com/auth/spreadsheets](https://www.googleapis.com/auth/spreadsheets)']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client.open("Data manager Paruise Shop")
