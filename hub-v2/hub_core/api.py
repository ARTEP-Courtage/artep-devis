"""
API du Hub — Hub Core V2
========================
Point d'entrée FastAPI. Expose les routes du hub.
En V2.2, la route /flux implémente le flux de preuve complet.
En V3, cette même API servira l'interface mobile vocale.

La route /sante est utilisée par le healthcheck Docker/Coolify.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from hub_core.routeur import router, TypeTache

app = FastAPI(
    title="Hub IA Multi-Sphères",
    description="Système d'exploitation des activités — orchestrateur V2",
    version="2.0.0",
)


# ---------------------------------------------------------------------------
# Santé — utilisée par Coolify pour vérifier que le conteneur tourne.
# ---------------------------------------------------------------------------
@app.get("/sante")
def sante():
    return {"statut": "ok", "version": "2.0.0"}


# ---------------------------------------------------------------------------
# Flux de preuve V2.2 (contrat défini ici, implémentation branchée sur
# le serveur). Le corps réel appellera : identification sphère -> lecture
# mémoire -> routage -> appel modèle -> réponse -> trace -> journal coût.
# ---------------------------------------------------------------------------
class DemandeFlux(BaseModel):
    sphere: str                       # ARTEP | KISIA | NAEV | SOCIOPRO | SOCLE
    message: str                      # la demande
    type_tache: str = "raisonnement"  # voir TypeTache
    forcer_provider: Optional[str] = None


@app.post("/flux")
def flux(demande: DemandeFlux):
    """
    Flux de preuve : montre le routage sans encore appeler l'IA
    (les appels réseau sont branchés en V2.2 sur le serveur).
    Déjà fonctionnel : la décision de routage est réelle.
    """
    try:
        type_tache = TypeTache(demande.type_tache)
    except ValueError:
        type_tache = TypeTache.RAISONNEMENT

    decision = router(type_tache, forcer=demande.forcer_provider)

    return {
        "sphere": demande.sphere,
        "routage": {
            "provider": decision.provider or "aucun",
            "classe_modele": decision.classe_modele or "n/a",
            "ia_requise": decision.ia_requise,
            "raison": decision.raison,
        },
        "etat": "routage résolu — appel modèle branché en V2.2",
    }


# ---------------------------------------------------------------------------
# Registre des routes prévues (documentation vivante).
# ---------------------------------------------------------------------------
@app.get("/")
def racine():
    return {
        "hub": "IA Multi-Sphères V2",
        "routes": {
            "GET /sante": "vérification de santé (healthcheck)",
            "POST /flux": "flux de preuve — routage d'une demande",
            "à venir V2.4": "GET /memoire, POST /memoire (mémoire automatisée)",
            "à venir V3": "interface mobile vocale",
        },
    }
