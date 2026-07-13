"""
Adaptateur Make — Hub IA V2
===========================
Make reste un EXÉCUTANT de flux, jamais le détenteur de la logique
métier. Le Hub Core déclenche des scénarios par webhook et lit leur
état par API si nécessaire.

Respecte l'audit ChatGPT : identifiant d'exécution commun, retours
normalisés, gestion des délais, répétition limitée, file d'échec.
Aucun secret en dur.
"""

import os
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class StatutExecution(Enum):
    DECLENCHE = "declenche"
    REUSSI = "reussi"
    ECHOUE = "echoue"
    EN_ATTENTE = "en_attente"


@dataclass
class ResultatMake:
    """Retour normalisé, identique quel que soit le scénario."""
    execution_id: str
    scenario: str
    statut: StatutExecution
    donnees: dict = field(default_factory=dict)
    erreur: Optional[str] = None


# Registre canonique des scénarios connus (référence -> webhook).
# Les URLs réelles viennent de l'environnement, jamais du code.
SCENARIOS = {
    "ARTEP_estimation":   "MAKE_HOOK_ARTEP_ESTIMATION",
    "ARTEP_controle":     "MAKE_HOOK_ARTEP_CONTROLE",
    "ARTEP_pvmv":         "MAKE_HOOK_ARTEP_PVMV",
    "NAEV_generation":    "MAKE_HOOK_NAEV_GENERATION",
    # complété au fil de V2 selon les besoins.
}


class MakeAdapter:
    """Traduit les demandes canoniques en déclenchements Make."""

    def __init__(self, timeout_s: int = 30, max_retries: int = 2):
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self._file_echec: list[ResultatMake] = []

    def _url_webhook(self, scenario: str) -> str:
        if scenario not in SCENARIOS:
            raise KeyError(f"Scénario inconnu : {scenario}")
        var_env = SCENARIOS[scenario]
        url = os.environ.get(var_env)
        if not url:
            raise RuntimeError(
                f"{var_env} absente. Définir l'URL du webhook dans Coolify."
            )
        return url

    def declencher(self, scenario: str, donnees: dict) -> ResultatMake:
        """
        Déclenche un scénario Make par webhook.
        Ajoute un execution_id commun pour la traçabilité (audit ChatGPT).
        Implémentation httpx réelle branchée en V2.2.
        """
        execution_id = str(uuid.uuid4())
        _ = self._url_webhook(scenario)  # valide la config
        raise NotImplementedError(
            f"declencher({scenario}) : contrat défini, appel httpx en V2.2. "
            f"execution_id={execution_id}, {len(donnees)} champs."
        )

    def file_echec(self) -> list[ResultatMake]:
        """Retourne les exécutions échouées à rejouer (audit ChatGPT)."""
        return list(self._file_echec)
