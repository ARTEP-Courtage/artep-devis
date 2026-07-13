# MODÈLE DE DONNÉES CANONIQUE — HUB IA MULTI-SPHÈRES

Version : V2.0-draft
Statut : fondation (aucune dépendance outil)
Référence supérieure : document Recadrage stratégique.

---

## 0. RAISON D'ÊTRE

Ce document définit les **entités du hub indépendamment de tout outil**.
Airtable, Make, OneDrive, Supabase ne sont que des *implémentations*
de ce modèle. Le modèle est l'actif ; les outils sont des interfaces
interchangeables.

Règle absolue : un agent ne connaît JAMAIS un identifiant de table
Airtable ou un webhook Make. Il ne connaît que les entités canoniques
ci-dessous. Un adaptateur traduit entre le canonique et l'outil réel.

Conséquence : le jour où Airtable est remplacé par PostgreSQL/Supabase,
seuls les adaptateurs changent. Les entités, les agents, la logique
métier et la mémoire restent identiques.

---

## 1. ENTITÉS CANONIQUES

### 1.1 Sphere
La sphère est le cloisonnement de premier niveau (multigestion sectorisée).
```
Sphere
  id            : identifiant stable (ARTEP | KISIA | NAEV | SOCIOPRO | SOCLE)
  nom           : libellé lisible
  type          : societe | holding | transverse
  couleur       : repère visuel de l'interface
  actif         : booléen
```
Valeurs actuelles : ARTEP, KISIA (DESICONCEPT), NAEV, SOCIOPRO
(holding de projets personnels), SOCLE (transverse, non-métier).

### 1.2 Decision (mémoire décisionnelle — C2 + C5)
```
Decision
  id                    : identifiant stable
  enonce                : la décision prise (quoi)
  sphere_id             : sphère propriétaire
  domaine               : Architecture | Mémoire | Amazon | Production |
                          Marketing | Finance | Juridique | Outils | Autre
  statut                : Actée | À trancher | En attente | Obsolète
  fiabilite             : Confirmée | Probable | Hypothèse
  source                : origine (chat, document, réunion)
  date_decision         : date
  lien_document         : référence documentaire (URL/chemin)
  # Couche C5 — le POURQUOI
  contexte              : situation au moment de la décision
  probleme_initial      : problème à résoudre
  raisonnement          : cheminement
  alternatives_etudiees : options écartées et pourquoi
  justification         : pourquoi cette option
  resultat_obtenu       : effet constaté (rempli après coup)
  date_validation       : dernière revalidation
  # Cloisonnement (risque 5 de l'audit)
  confidentialite       : public | interne | sensible
  agents_autorises      : catégories d'agents autorisées à lire
  croisement_transverse : booléen — la décision peut-elle être croisée
                          entre sphères par la recherche transversale
```

### 1.3 Agent (registre — collaborateurs numériques)
```
Agent
  id                : AGT-xxx
  nom               : libellé
  version           : semver interne
  sphere_id         : sphère de rattachement
  mission           : une phrase
  perimetre_fait    : ce que l'agent fait
  perimetre_ne_fait_pas : frontière anti-doublon
  entrees           : sources attendues
  sorties           : livrables produits
  ia_affectee       : Claude | OpenAI | Gemini | OpenSource | Aucune
  prompt_ref        : chemin du .md versionné (JAMAIS le prompt en dur)
  dependances       : agents/services requis
  scenario_make     : référence d'exécution (via adaptateur)
  priorite_roi      : entier (0 = plus haute)
  niveau_autonomie  : 0 lecture | 1 proposition | 2 action après validation |
                      3 action auto non sensible | 4 interdit au départ
  validation_humaine: booléen — requise avant action engageante
  survit_sans_dirigeant : booléen (principe de conception santé)
  statut            : Actif | En construction | À construire | Obsolète
```

### 1.4 MemoireAmelioration (C6)
```
Amelioration
  id            : identifiant
  element       : ce qui est observé
  type          : Erreur | Correction | Prompt performant | Coût |
                  Performance | Recommandation
  sphere_id     : sphère concernée
  ia_concernee  : Claude | OpenAI | Gemini | OpenSource | Aucune
  impact        : Élevé | Moyen | Faible
  date          : date
  detail        : description
```

### 1.5 Observabilite (C7)
```
Observabilite
  id             : identifiant
  mesure         : ce qui est mesuré
  type_mesure    : Coût | Temps de réponse | Taux de réussite |
                   Taux d'erreur | Appels API | Consommation mémoire | ROI
  sphere_id      : sphère
  agent_id       : agent concerné
  ia_utilisee    : modèle appelé
  valeur         : nombre
  unite          : euros | secondes | pourcentage | opérations
  date_mesure    : date
  commentaire    : contexte
```

### 1.6 Conversation (C1 — mémoire conversationnelle)
```
Conversation
  id            : identifiant
  sphere_id     : sphère
  date          : horodatage
  resume        : synthèse de l'échange
  decisions_ref : décisions issues de cet échange
  source_chat   : chat d'origine (Claude/ChatGPT + sujet)
```
Note : en V2, chaque appel API étant sans mémoire, c'est l'orchestrateur
qui reconstitue le contexte à partir de cette entité + injection.

### 1.7 Document (C3 — mémoire documentaire, référence seulement)
```
Document
  id            : identifiant
  titre         : nom
  sphere_id     : sphère
  type          : contrat | devis | étude | règle | procédure | prompt
  chemin_source : emplacement réel (OneDrive), jamais le contenu
  date          : date
  hash          : empreinte de version
```

---

## 2. RÈGLES DE COHÉRENCE

R1. Une donnée = une seule source de vérité. Pas de duplication entre
    sphères. Le croisement se fait par référence, jamais par copie.

R2. Cloisonnement par défaut. Une entrée n'est visible hors de sa sphère
    que si `croisement_transverse = vrai` ET que l'agent demandeur figure
    dans `agents_autorises`. La transversalité n'est jamais un accès
    universel.

R3. Aucune logique métier dans un outil. Les règles vivent dans /rules
    (fichiers .md versionnés). Les outils exécutent, ne décident pas.

R4. Aucun secret dans le modèle. Ni clé API, ni mot de passe dans une
    entité. Les secrets vivent dans les variables d'environnement
    chiffrées (Coolify).

R5. Traçabilité obligatoire. Toute Decision porte source + date +
    fiabilité + statut. Aucune mémorisation stratégique sans traçabilité.

R6. Principe de conception santé. Tout Agent porte `survit_sans_dirigeant`.
    Un seul projet a le droit d'avoir cette valeur à « non » (le N1).

---

## 3. MAPPING VERS LES IMPLÉMENTATIONS ACTUELLES

Le modèle canonique est aujourd'hui implémenté ainsi (via adaptateurs) :

| Entité canonique   | Implémentation V1 (Airtable)                          |
|--------------------|-------------------------------------------------------|
| Decision           | base HUB — Mémoire centrale / table Mémoire_Décisions  |
| Amelioration       | base HUB / table Amélioration_Continue                 |
| Observabilite      | base HUB / table Observabilité                         |
| Agent              | base PMO Orchestrateur / table Architecture            |
| Document           | OneDrive (référence) + champ lien dans Airtable        |
| Conversation       | à créer (table Mémoire_Conversations)                  |
| Sphere             | champ Société dans chaque table                        |

Quand la mémoire vectorielle sera ajoutée (service géré séparé), une
entité `Embedding` liera chaque Decision/Document à son vecteur, sans
modifier les entités ci-dessus.

---

## 4. CE QUI RESTE À FAIRE EN V2.0

- [ ] Créer l'entité Conversation dans l'implémentation (table Airtable).
- [ ] Ajouter les champs de cloisonnement (confidentialite, agents_autorises,
      croisement_transverse) à Mémoire_Décisions.
- [ ] Ajouter survit_sans_dirigeant au registre Architecture.
- [ ] Écrire les adaptateurs (Airtable, Make) qui traduisent canonique <-> outil.
- [ ] Écrire les fichiers de règles /rules/*.md (externalisation des prompts).

FIN DU MODÈLE CANONIQUE V2.0-draft.
