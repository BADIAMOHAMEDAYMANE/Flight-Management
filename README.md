# ✈️ Flight Tracker & AI Travel Assistant

<p align="left">
  <img src="https://img.shields.io/badge/React-20232a?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Gemini-API-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white" />
  <img src="https://img.shields.io/badge/AviationStack-API-009688?style=for-the-badge" />
</p>

Application web de **suivi de vols en temps réel** couplée à un **assistant de voyage conversationnel** (IA générative).

---

## 🚀 Fonctionnalités

### Suivi des vols (React + API AviationStack)
- **Destinations au départ du Maroc** : liste des destinations desservies (vols `dep_country=MA`), dédoublonnées, avec affichage progressif (« voir plus »).
- **Vols en temps réel** : recherche par **numéro de vol IATA** (ex. `AT200`) ou par **compagnie aérienne**.
- **Filtres et tri** : statut du vol (en vol, programmé, atterri, annulé), tri par heure de départ ou d'arrivée.
- **Pagination** (10 vols par page), heure de dernière mise à jour et bouton d'actualisation.
- Gestion des erreurs et de l'indisponibilité de l'API.

### Assistant de voyage « TravelMate » (Flask + Google Gemini)
- Backend **Flask** exposant une API REST `POST /api/chat`.
- **Prompt système** dédié : 1 à 3 suggestions de destinations, avec le type de voyageurs et la meilleure saison.
- **Historique par session** (identifiant de session côté client), limité aux 20 derniers messages.

---

## 🏗️ Architecture

```
Navigateur (React + Vite)
   ├── Body / TravelPlan ──► API AviationStack (données de vol en temps réel)
   └── Chatbot ───────────► Backend Flask  POST /api/chat ──► API Google Gemini
```

---

## 🗂️ Structure du projet

```
Flight-Management/
├── src/
│   ├── App.jsx                 # Mise en page : navbar, vols, assistant
│   ├── Navbar/                 # Navigation + ouverture de l'assistant
│   ├── Body/                   # Destinations au départ du Maroc
│   ├── TravelPlan/             # Recherche, filtres, tri et pagination des vols
│   ├── Chatbot/                # Interface de l'assistant TravelMate
│   └── Footer/
├── backend/
│   ├── app.py                  # API Flask + Gemini
│   ├── requirements.txt
│   └── .env.example
├── .env.example                # Clés côté frontend (Vite)
├── package.json
└── vite.config.js
```

---

## ⚙️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/BADIAMOHAMEDAYMANE/Flight-Management.git
cd Flight-Management
```

### 2. Clés d'API

```bash
cp .env.example .env                  # VITE_AVIATIONSTACK_KEY=...
cp backend/.env.example backend/.env  # GEMINI_API_KEY=...
```

> ⚠️ Les variables préfixées par `VITE_` sont intégrées au bundle du navigateur : n'y mettez jamais de clé sensible en production.

### 3. Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
python app.py                 # http://localhost:5000
```

### 4. Frontend (React)

```bash
npm install
npm run dev                   # http://localhost:5173
```

---

## 🔮 Améliorations possibles

- Persister l'historique des conversations dans une base de données (aujourd'hui en mémoire).
- Passer les appels AviationStack par le backend pour ne plus exposer la clé côté navigateur.
- Ajouter le routage (React Router) et des tests.

---

## 👤 Auteur

**Mohamed Aymane Badia** — élève ingénieur en 5ᵉ année, IA & Data Science (EMSI)
