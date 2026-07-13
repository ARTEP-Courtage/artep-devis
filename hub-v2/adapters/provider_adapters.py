"""
Provider Adapters — Hub IA V2
=============================
Interface NEUTRE pour tous les fournisseurs d'IA. Le Hub Core demande
une complétion sans savoir quel modèle répond. Changer de modèle =
changer une valeur de configuration, jamais réécrire un agent.

Respecte le principe P1 (remplaçabilité) et P2 (capacité maximale,
le coût est un garde-fou). Chaque provider normalise sa réponse vers
le format commun CompletionResult.

Aucune clé API en dur : toutes lues depuis l'environnement.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CompletionResult:
    """Format de réponse commun à tous les providers."""
    texte: str
    modele: str
    provider: str
    tokens_entree: int = 0
    tokens_sortie: int = 0
    cout_estime_eur: float = 0.0
    duree_ms: int = 0
    meta: dict = field(default_factory=dict)


class ProviderAdapter(ABC):
    """Contrat que tout fournisseur d'IA doit respecter."""

    nom: str = "abstrait"

    @abstractmethod
    def completer(self, prompt: str, systeme: Optional[str] = None,
                  modele: Optional[str] = None) -> CompletionResult:
        ...

    def _cle(self, var_env: str) -> str:
        cle = os.environ.get(var_env)
        if not cle:
            raise RuntimeError(
                f"{var_env} absente. Définir dans Coolify (jamais dans le code)."
            )
        return cle


class AnthropicAdapter(ProviderAdapter):
    """Claude — raisonnement, architecture, arbitrages (Opus)."""
    nom = "anthropic"
    MODELE_DEFAUT = "claude-opus"      # résolu en identifiant réel en V2.2

    def completer(self, prompt, systeme=None, modele=None) -> CompletionResult:
        _ = self._cle("ANTHROPIC_API_KEY")
        raise NotImplementedError(
            "AnthropicAdapter : contrat défini, appel SDK en V2.2."
        )


class OpenAIAdapter(ProviderAdapter):
    """GPT — code, vision, extraction structurée."""
    nom = "openai"
    MODELE_DEFAUT = "gpt-structure"

    def completer(self, prompt, systeme=None, modele=None) -> CompletionResult:
        _ = self._cle("OPENAI_API_KEY")
        raise NotImplementedError(
            "OpenAIAdapter : contrat défini, appel SDK en V2.2."
        )


class GeminiAdapter(ProviderAdapter):
    """Gemini — écosystème Google (ajouté seulement si un usage le justifie)."""
    nom = "gemini"
    MODELE_DEFAUT = "gemini"

    def completer(self, prompt, systeme=None, modele=None) -> CompletionResult:
        _ = self._cle("GEMINI_API_KEY")
        raise NotImplementedError(
            "GeminiAdapter : contrat défini, appel SDK en V2.2."
        )


class OpenSourceAdapter(ProviderAdapter):
    """Open source (Mistral/Groq via API tierce) — masse triviale."""
    nom = "opensource"
    MODELE_DEFAUT = "mistral"

    def completer(self, prompt, systeme=None, modele=None) -> CompletionResult:
        _ = self._cle("OPENSOURCE_API_KEY")
        raise NotImplementedError(
            "OpenSourceAdapter : contrat défini, appel API en V2.2."
        )


# Registre des providers disponibles, résolu par le Hub Core.
PROVIDERS = {
    "anthropic":  AnthropicAdapter,
    "openai":     OpenAIAdapter,
    "gemini":     GeminiAdapter,
    "opensource": OpenSourceAdapter,
}


def get_provider(nom: str) -> ProviderAdapter:
    if nom not in PROVIDERS:
        raise KeyError(f"Provider inconnu : {nom}")
    return PROVIDERS[nom]()
