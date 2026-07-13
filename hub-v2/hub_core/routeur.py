"""
Routeur IA — Hub Core V2
========================
Choisit le modèle le plus adapté à une tâche. Incarne le principe P2 :
routage par CAPACITÉ/valeur produite, pas par coût. Le coût est un
garde-fou (plafonds), jamais le critère de sélection.

Doctrine (issue de la mémoire, sphère SOCIOPRO) :
- Opus       : pilotage, arbitrages, raisonnement long, architecture.
- Sonnet     : production quotidienne.
- Haiku      : micro-tâches haute fréquence.
- OpenAI     : code, vision, extraction structurée.
- OpenSource : masse triviale (tri, classification, reformulation).
- Aucune IA  : si une règle déterministe suffit (modèle AGT-007).

Le routeur ne contient AUCUN identifiant de modèle réel : il renvoie
un provider + une classe de modèle. Les Provider Adapters résolvent
l'identifiant réel. Ainsi un changement de gamme ne touche pas ce fichier.
"""

from dataclasses import dataclass
from enum import Enum


class TypeTache(Enum):
    RAISONNEMENT = "raisonnement"        # juridique, stratégie, audit, archi
    PRODUCTION = "production"            # rédaction courante, fiches
    CODE = "code"                        # code, extraction structurée, vision
    MASSE = "masse"                      # tri, classification, reformulation
    DETERMINISTE = "deterministe"        # règle pure, pas d'IA
    MICRO = "micro"                      # micro-tâche haute fréquence


@dataclass
class DecisionRoutage:
    provider: str          # clé du registre PROVIDERS
    classe_modele: str     # "opus" | "sonnet" | "haiku" | ...
    ia_requise: bool
    raison: str            # journalisée (audit ChatGPT : tracer le choix)


# Table de routage par défaut. Modifiable sans toucher au code appelant.
_ROUTAGE = {
    TypeTache.RAISONNEMENT:  DecisionRoutage("anthropic", "opus",   True,
        "Raisonnement long / arbitrage : capacité maximale requise."),
    TypeTache.PRODUCTION:    DecisionRoutage("anthropic", "sonnet", True,
        "Production quotidienne : bon rapport capacité/débit."),
    TypeTache.CODE:          DecisionRoutage("openai",    "structure", True,
        "Code / vision / extraction structurée : outillage OpenAI."),
    TypeTache.MASSE:         DecisionRoutage("opensource","mistral", True,
        "Volume trivial : open source économique (garde-fou coût)."),
    TypeTache.MICRO:         DecisionRoutage("anthropic", "haiku",  True,
        "Micro-tâche haute fréquence : modèle rapide."),
    TypeTache.DETERMINISTE:  DecisionRoutage("",          "",       False,
        "Règle déterministe suffisante : aucune IA (modèle AGT-007)."),
}


def router(type_tache: TypeTache, forcer: str | None = None) -> DecisionRoutage:
    """
    Renvoie la décision de routage pour une tâche.
    `forcer` permet au dirigeant d'imposer un provider (override manuel,
    exigé par l'audit ChatGPT V2.3).
    """
    if forcer:
        return DecisionRoutage(
            provider=forcer, classe_modele="", ia_requise=True,
            raison=f"Modèle forcé manuellement : {forcer}.",
        )
    if type_tache not in _ROUTAGE:
        # Par défaut, on ne descend jamais en gamme sur une tâche inconnue :
        # principe P2, capacité maximale prime.
        return _ROUTAGE[TypeTache.RAISONNEMENT]
    return _ROUTAGE[type_tache]
