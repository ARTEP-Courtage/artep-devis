# HUB IA MULTI-SPHÈRES — Dépôt V2

Système d'exploitation des activités du dirigeant sur 10 ans.
Ce n'est pas un projet informatique : l'architecture technique est un
moyen. Référence supérieure : document Recadrage stratégique.

## Sphères pilotées
ARTEP (courtage travaux) · KISIA/DESICONCEPT (sportswear Amazon) ·
NAEV (artiste virtuel) · SOCIOPRO (holding de projets personnels) ·
SOCLE (transverse).

## Principes non négociables
1. Indépendance / remplaçabilité totale de chaque brique.
2. Capacité IA maximale ; le coût est un garde-fou, pas un critère.
3. Multigestion sectorisée (cloisonnement par sphère).
4. Aucune logique métier dans un outil (règles en /rules/*.md).
5. Mémoire transversale à 7 couches, auto-enrichissante.
6. Motif du passage API : contrôle et évolution, jamais l'économie.
7. Conception santé : un seul projet dépend de la présence du dirigeant.

## Structure du dépôt
```
docs/        MODELE_DONNEES_CANONIQUE.md, ARCHITECTURE.md
hub_core/    cœur métier (sans dépendance outil)
adapters/    provider / tool / memory adapters
agents/      définitions d'agents (référencent /rules)
rules/       prompts et règles métier versionnés (.md)
tests/       tests unitaires et d'intégration
```

## Stack
Python 3.12 · FastAPI · LangGraph (derrière adaptateur) ·
Docker/Compose · Git · Coolify sur IONOS VPS L+ (Ubuntu 24.04, UE).

## État
V2.0 en cours — préparation indépendante du serveur.
Aucune commande de serveur requise à ce stade.

## Déploiement (à partir de V2.1)
Coolify (couche visuelle) + Claude Code/Codex (exécutant) +
dirigeant (gestes incompressibles : créer le serveur, saisir les
accès, valider les mises en production importantes). Aucun prestataire.
