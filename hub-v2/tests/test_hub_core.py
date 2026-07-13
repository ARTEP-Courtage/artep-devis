"""
Tests V2.0 — routeur et contrôle des coûts.
Vérifient la logique métier SANS aucun appel réseau ni serveur.
Lançables localement : python -m pytest tests/
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hub_core.routeur import router, TypeTache, DecisionRoutage
from hub_core.controle_couts import Budget, ControleurCouts, NiveauAlerte


# ---------- Routeur ----------

def test_raisonnement_va_vers_opus():
    d = router(TypeTache.RAISONNEMENT)
    assert d.provider == "anthropic"
    assert d.classe_modele == "opus"
    assert d.ia_requise is True

def test_masse_va_vers_opensource():
    d = router(TypeTache.MASSE)
    assert d.provider == "opensource"

def test_deterministe_sans_ia():
    d = router(TypeTache.DETERMINISTE)
    assert d.ia_requise is False

def test_override_manuel():
    d = router(TypeTache.MASSE, forcer="anthropic")
    assert d.provider == "anthropic"
    assert "forcé" in d.raison.lower()


# ---------- Contrôle des coûts ----------

def test_budget_autorise_sous_plafond():
    b = Budget("AGT-001", plafond_quotidien_eur=10, plafond_mensuel_eur=100)
    assert b.autorise(5) is True

def test_budget_refuse_tache_non_critique_au_plafond():
    b = Budget("AGT-001", plafond_quotidien_eur=10, plafond_mensuel_eur=100)
    b.enregistrer(10)
    assert b.autorise(1, tache_critique=False) is False

def test_budget_laisse_passer_tache_critique():
    b = Budget("AGT-001", plafond_quotidien_eur=10, plafond_mensuel_eur=100)
    b.enregistrer(10)
    assert b.autorise(1, tache_critique=True) is True

def test_niveaux_alerte():
    b = Budget("S", plafond_quotidien_eur=100, plafond_mensuel_eur=1000)
    assert b.niveau() == NiveauAlerte.OK
    b.enregistrer(50)
    assert b.niveau() == NiveauAlerte.ALERTE_50
    b.enregistrer(25)
    assert b.niveau() == NiveauAlerte.ALERTE_75
    b.enregistrer(15)
    assert b.niveau() == NiveauAlerte.ALERTE_90

def test_controleur_deux_niveaux():
    c = ControleurCouts()
    c.budgets_agent["AGT-005"] = Budget("AGT-005", 5, 50)
    c.budgets_sphere["ARTEP"] = Budget("ARTEP", 20, 200)
    ok, alertes = c.verifier("AGT-005", "ARTEP", cout_eur=3)
    assert ok is True


if __name__ == "__main__":
    # Exécution directe sans pytest.
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    reussis = 0
    for t in tests:
        try:
            t()
            print(f"  OK   {t.__name__}")
            reussis += 1
        except Exception:
            print(f"  FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{reussis}/{len(tests)} tests réussis.")
