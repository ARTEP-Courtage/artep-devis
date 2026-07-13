# RÈGLES & PROMPTS EXTERNALISÉS

Ce dossier contient les prompts système et règles métier de chaque
agent, en fichiers .md versionnés. **Aucun prompt ne doit vivre en dur
dans un scénario Make ou dans le code.** Modèle de référence : l'agent
NAEV, seul agent V1 déjà conforme.

## Pourquoi
Externaliser les prompts rend les agents remplaçables (principe P1) :
changer d'IA ou modifier un comportement = éditer un fichier texte,
sans toucher au code ni au scénario.

## Convention de nommage
```
rules/<AGENT_ID>_<nom_court>.md      → prompt système de l'agent
rules/shared_<domaine>.md            → règles partagées (ex. juridique)
rules/thresholds_<sphere>.md         → seuils chiffrés d'une sphère
```

## Format d'un fichier de prompt
```
# <AGENT_ID> — <nom>
Version : x.y
Sphère : ARTEP | KISIA | NAEV | SOCIOPRO | SOCLE

## Rôle
<une phrase>

## Fait
<périmètre positif>

## Ne fait pas
<frontière anti-doublon>

## Règles
<contraintes métier>

## Validation humaine
<ce qui exige un accord avant action>
```

## Migration à faire (V1.5 → V2.0)
Les 7 agents ARTEP ont leur prompt enfoui dans les modules GPT de Make.
Chaque prompt doit être extrait ici, puis le scénario Make modifié pour
lire le .md (via OneDrive) au lieu de contenir le prompt en dur.
Ordre suggéré (par priorité ROI) : AGT-001, AGT-006, AGT-005, AGT-007,
AGT-002, AGT-003, AGT-004.
