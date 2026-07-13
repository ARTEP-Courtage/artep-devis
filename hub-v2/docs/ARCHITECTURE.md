# ARCHITECTURE TECHNIQUE — HUB IA V2

Version : V2.0-draft
Stack validée (audit ChatGPT) : Python 3.12 · FastAPI · LangGraph
derrière adaptateur · Docker/Compose · Git · Coolify sur IONOS.

Principe directeur : **rien de métier ne dépend d'un outil.** Chaque
couche est remplaçable sans réécrire les autres.

---

## 1. VUE EN COUCHES

```
┌─────────────────────────────────────────────────────────┐
│  INTERFACE (V3)  — PWA mobile + vocal + multilingue       │
│  (non construite en V2 ; FastAPI expose déjà les routes)  │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│  HUB CORE  (le cœur, sans dépendance outil)               │
│   - modèle de données canonique                           │
│   - règles métier (chargées depuis /rules/*.md)           │
│   - mémoire (7 couches, logique d'accès + cloisonnement)  │
│   - registre d'agents                                     │
│   - contrôle des coûts (budgets, plafonds, alertes)       │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│  ORCHESTRATOR ADAPTER  (interface neutre d'orchestration) │
│   └─ LangGraph Adapter (implémentation actuelle)          │
│      remplaçable sans toucher au Hub Core                 │
└───────────────────────────┬─────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌────────────────┐  ┌──────────────────┐
│ PROVIDER       │  │ TOOL ADAPTERS  │  │ MEMORY ADAPTERS  │
│ ADAPTERS       │  │                │  │                  │
│ - Anthropic    │  │ - Airtable     │  │ - Airtable (C2/  │
│ - OpenAI       │  │ - Make         │  │   C5/C6/C7)      │
│ - Gemini       │  │ - OneDrive     │  │ - Vectoriel      │
│ - OpenSource   │  │ - Publer       │  │   (service géré, │
│                │  │ - Amazon       │  │    ajouté V1.5)  │
└───────────────┘  └────────────────┘  └──────────────────┘
```

---

## 2. RÔLE DE CHAQUE COUCHE

### Hub Core
Le seul endroit où vit la logique métier. Ne connaît aucun outil
concret : il parle en entités canoniques. Contient le routage cognitif
(quel modèle pour quelle tâche), la logique de mémoire (quoi lire, quoi
écrire, quel cloisonnement), le registre, le contrôle des coûts.

### Orchestrator Adapter
Interface neutre. Le Hub Core demande « exécute ce flux » sans savoir
que c'est LangGraph derrière. Si LangGraph est remplacé, seul cet
adaptateur change. **LangGraph ne contient jamais : règles métier,
prompts, identifiants de tables, décisions de routage irréversibles.**

### Provider Adapters
Un adaptateur par fournisseur d'IA. Le modèle est un paramètre.
Changer de modèle = changer une valeur, pas réécrire un agent.
Chaque adaptateur normalise entrée/sortie vers un format commun.

### Tool Adapters
Un adaptateur par outil externe. L'adaptateur Airtable est le SEUL
composant autorisé à connaître les identifiants de bases/tables, les
champs techniques, la pagination, les limites d'appel. Ainsi Airtable
est remplaçable sans réécrire les agents.
Make : déclenché par webhooks ; son état lu via API si nécessaire.
Make reste exécutant de flux, jamais détenteur de logique.

### Memory Adapters
Séparés des Tool Adapters car la mémoire a sa logique propre
(cloisonnement, croisement transverse, statuts). Le vectoriel est un
Memory Adapter ajouté plus tard, en service géré séparé du serveur.

---

## 3. FLUX DE PREUVE V2.2 (premier flux à déployer)

Le flux minimal qui prouve que la chaîne complète fonctionne :

```
1. Réception d'une demande (route FastAPI)
2. Identification de la sphère (Hub Core)
3. Lecture d'une donnée en mémoire (Memory Adapter → Airtable)
4. Appel d'UN seul modèle (Provider Adapter → Anthropic)
5. Production d'une réponse (Hub Core)
6. Écriture d'une trace (Memory Adapter → Airtable)
7. Journalisation du coût et de la durée (Observabilité)
```
Aucune orchestration complexe à cette étape. Objectif : prouver la
chaîne bout en bout, pas la richesse.

---

## 4. SÉQUENÇAGE V2

- **V2.0** — préparation sans serveur : dépôt Git, ce modèle, /rules,
  Docker, tests, variables d'env, procédure de restauration. ← EN COURS
- **V2.1** — infra minimale : VPS L+, Ubuntu 24.04, SSH, pare-feu,
  Coolify, Git connecté, domaine, HTTPS, sauvegarde initiale.
- **V2.2** — orchestrateur minimal : le flux de preuve ci-dessus.
- **V2.3** — routage multi-modèles : Anthropic + OpenAI + (Gemini si
  justifié), règles de sélection, repli, plafonds, journal du choix.
- **V2.4** — mémoire automatisée : récupération de contexte, écriture
  contrôlée, statuts, doublons, cloisonnement strict des sphères.
- **V2.5** — agent d'entretien à autonomie progressive (5 niveaux).

---

## 5. ENVIRONNEMENTS (risque 2 de l'audit)

Jamais de modification directe en production par une IA.
- **dev** — développement
- **preprod** — validation
- **prod** — production

Au départ, dev et preprod peuvent partager le serveur avec des
conteneurs séparés. Tout changement passe par : dépôt Git → branche →
demande de fusion → tests → historique → possibilité de retour arrière.

---

## 6. SÉCURITÉ & COÛTS (dès le premier appel)

Secrets : variables d'environnement chiffrées dans Coolify. Aucune clé
dans le code, dans Airtable, ni dans les .md. Rotation régulière,
droits minimaux, journalisation sans jamais enregistrer les secrets.

Coûts : budget par agent + par sphère, plafond quotidien + mensuel,
alertes à 50/75/90/100 %, arrêt automatique des tâches non critiques,
journal du coût estimé et réel.

FIN DE L'ARCHITECTURE V2.0-draft.
