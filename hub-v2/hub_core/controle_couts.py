"""
Contrôle des coûts — Hub Core V2
================================
Répond au risque 8 de l'audit ChatGPT : budget par agent, par sphère,
plafonds quotidien/mensuel, alertes à 50/75/90/100 %, arrêt automatique
des tâches non critiques.

Actif DÈS le premier appel API. Ne stocke jamais de secret : uniquement
des compteurs de coût.
"""

from dataclasses import dataclass, field
from enum import Enum


class NiveauAlerte(Enum):
    OK = "ok"
    ALERTE_50 = "50%"
    ALERTE_75 = "75%"
    ALERTE_90 = "90%"
    PLAFOND = "100%"


@dataclass
class Budget:
    """Budget d'une entité (agent ou sphère)."""
    identifiant: str
    plafond_quotidien_eur: float
    plafond_mensuel_eur: float
    consomme_jour_eur: float = 0.0
    consomme_mois_eur: float = 0.0

    def niveau(self) -> NiveauAlerte:
        ratio = max(
            self.consomme_jour_eur / self.plafond_quotidien_eur
            if self.plafond_quotidien_eur else 0,
            self.consomme_mois_eur / self.plafond_mensuel_eur
            if self.plafond_mensuel_eur else 0,
        )
        if ratio >= 1.0:
            return NiveauAlerte.PLAFOND
        if ratio >= 0.9:
            return NiveauAlerte.ALERTE_90
        if ratio >= 0.75:
            return NiveauAlerte.ALERTE_75
        if ratio >= 0.5:
            return NiveauAlerte.ALERTE_50
        return NiveauAlerte.OK

    def autorise(self, cout_eur: float, tache_critique: bool = False) -> bool:
        """
        Autorise ou refuse une dépense.
        Une tâche critique passe même au plafond (mais alerte) ;
        une tâche non critique est stoppée au plafond.
        """
        projete_jour = self.consomme_jour_eur + cout_eur
        projete_mois = self.consomme_mois_eur + cout_eur
        depasse = (
            (self.plafond_quotidien_eur and projete_jour > self.plafond_quotidien_eur)
            or (self.plafond_mensuel_eur and projete_mois > self.plafond_mensuel_eur)
        )
        if depasse and not tache_critique:
            return False
        return True

    def enregistrer(self, cout_eur: float) -> None:
        self.consomme_jour_eur += cout_eur
        self.consomme_mois_eur += cout_eur


@dataclass
class ControleurCouts:
    """Agrège les budgets par agent et par sphère."""
    budgets_agent: dict = field(default_factory=dict)
    budgets_sphere: dict = field(default_factory=dict)

    def verifier(self, agent_id: str, sphere_id: str,
                 cout_eur: float, critique: bool = False) -> tuple[bool, list]:
        """
        Vérifie qu'une dépense est autorisée aux deux niveaux.
        Renvoie (autorisé, [alertes]).
        """
        alertes = []
        for cle, registre in ((agent_id, self.budgets_agent),
                              (sphere_id, self.budgets_sphere)):
            budget = registre.get(cle)
            if budget is None:
                continue
            if not budget.autorise(cout_eur, critique):
                return False, [f"Plafond atteint pour {cle}"]
            niveau = budget.niveau()
            if niveau != NiveauAlerte.OK:
                alertes.append(f"{cle} : {niveau.value}")
        return True, alertes

    def enregistrer(self, agent_id: str, sphere_id: str, cout_eur: float) -> None:
        for cle, registre in ((agent_id, self.budgets_agent),
                              (sphere_id, self.budgets_sphere)):
            if cle in registre:
                registre[cle].enregistrer(cout_eur)
