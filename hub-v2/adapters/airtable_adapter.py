"""
Adaptateur Airtable — Hub IA V2
================================
SEUL composant autorisé à connaître les identifiants de bases, de
tables et de champs Airtable. Traduit entre les entités canoniques
(voir docs/MODELE_DONNEES_CANONIQUE.md) et l'API Airtable réelle.

Conséquence du découplage : si Airtable est remplacé par PostgreSQL
ou Supabase, seul CE fichier change. Les agents, le Hub Core et la
logique métier restent identiques.

Règles respectées :
- Aucune clé API dans ce fichier (lue depuis les variables d'env).
- Aucune logique métier ici : uniquement de la traduction.
- Le reste du hub n'importe JAMAIS d'identifiant Airtable directement.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional


# ---------------------------------------------------------------------------
# MAPPING CANONIQUE <-> AIRTABLE
# Le seul endroit du hub où vivent les identifiants réels.
# Renseignés à partir de l'implémentation V1 existante.
# ---------------------------------------------------------------------------

BASE_MEMOIRE = "app4aNS6aj0zbwpX2"          # HUB — Mémoire centrale
BASE_PMO = "appz6zAUM1msEsjOp"              # PMO Orchestrateur (registre agents)

TABLES = {
    # entité canonique   ->   (base_id, table_id)
    "Decision":       (BASE_MEMOIRE, "tblIj25n1kOfqi7Q2"),
    "Amelioration":   (BASE_MEMOIRE, "tblMdFKKHbt9WInqN"),
    "Observabilite":  (BASE_MEMOIRE, "tblCQcF58XzpEW0S7"),
    "Agent":          (BASE_PMO,     "tblsQ6E6yuq73gHZ1"),
}

# Traduction des champs canoniques vers les field_id Airtable.
# Volontairement partiel : complété au fil de V2.0.
FIELDS = {
    "Decision": {
        "enonce":                "fldWGrZsghsxbNBKN",
        "sphere_id":             "fldBt3boSPfwqT1ij",
        "domaine":               "fld6oF66c9okt7nFF",
        "statut":                "fld2h2fXI9eW2Txpb",
        "fiabilite":             "fldwXmykvwW5uJa3n",
        "source":                "fldurpfHkSPrIha74",
        "date_decision":         "fld0memL5F9pEx0AT",
        "contexte":              "fldPUu5XCHR0Plh8l",
        "probleme_initial":      "fldfGitRSMY6tKcvU",
        "raisonnement":          "fldjnxLklE3L0y49H",
        "alternatives_etudiees": "fldHGuzt80aDdVfIk",
        "justification":         "fldnCyPzh5hwmvIvE",
        "resultat_obtenu":       "fldzrLtV9bqRntMAr",
    },
}


@dataclass
class AirtableConfig:
    """Configuration lue depuis l'environnement — jamais en dur."""
    api_key: str

    @classmethod
    def from_env(cls) -> "AirtableConfig":
        key = os.environ.get("AIRTABLE_API_KEY")
        if not key:
            raise RuntimeError(
                "AIRTABLE_API_KEY absente de l'environnement. "
                "Définir la variable dans Coolify (jamais dans le code)."
            )
        return cls(api_key=key)


class AirtableAdapter:
    """
    Traduit les opérations canoniques en appels Airtable.
    Le Hub Core appelle read()/write() avec des noms d'ENTITÉS
    canoniques, jamais avec des identifiants Airtable.
    """

    def __init__(self, config: Optional[AirtableConfig] = None):
        self._config = config or AirtableConfig.from_env()

    def _resolve(self, entite: str) -> tuple[str, str]:
        if entite not in TABLES:
            raise KeyError(f"Entité canonique inconnue : {entite}")
        return TABLES[entite]

    def _to_airtable_fields(self, entite: str, data: dict) -> dict:
        """Traduit les clés canoniques -> field_id Airtable."""
        mapping = FIELDS.get(entite, {})
        out = {}
        for cle_canonique, valeur in data.items():
            field_id = mapping.get(cle_canonique)
            if field_id is None:
                # champ non encore mappé : ignoré proprement plutôt
                # que d'écrire un champ inconnu.
                continue
            out[field_id] = valeur
        return out

    def read(self, entite: str, filtre: Optional[dict] = None) -> list[dict]:
        """
        Lit des enregistrements canoniques.
        Implémentation réelle (pyairtable) ajoutée en V2.2 ;
        ici on fixe le CONTRAT d'interface.
        """
        base_id, table_id = self._resolve(entite)
        raise NotImplementedError(
            f"read({entite}) : contrat défini, implémentation pyairtable "
            f"en V2.2. Cible base={base_id} table={table_id}."
        )

    def write(self, entite: str, data: dict) -> dict:
        """Écrit un enregistrement canonique."""
        base_id, table_id = self._resolve(entite)
        fields = self._to_airtable_fields(entite, data)
        raise NotImplementedError(
            f"write({entite}) : contrat défini, implémentation en V2.2. "
            f"Cible base={base_id} table={table_id}, "
            f"{len(fields)} champs traduits."
        )


# Point d'extension : un futur PostgresAdapter/SupabaseAdapter
# implémentera la MÊME interface read()/write(), et le Hub Core
# n'aura rien à changer.
