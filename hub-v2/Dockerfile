# Hub IA V2 — image applicative
# Python 3.12 (stack validée par l'audit ChatGPT).
FROM python:3.12-slim

WORKDIR /app

# Dépendances d'abord (cache Docker).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code applicatif.
COPY . .

# Aucune clé ici : les secrets viennent des variables d'environnement
# chiffrées de Coolify.

EXPOSE 8000

# L'API démarre ici (route de santé disponible dès V2.2).
CMD ["uvicorn", "hub_core.api:app", "--host", "0.0.0.0", "--port", "8000"]
