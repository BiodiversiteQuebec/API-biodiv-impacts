### Installation
- Make sure you have Python 3.12 (maybe other versions will work but i tested with 3.12)

```
python3 -m venv .venv
source .venv/bin/activate

set -a
source .env
set +a
python3 -m pip install -r requirements.txt

```

### Updating only the bq_impact_indicators package
```
set -a && source .env && set +a
python3 -m pip install --force-reinstall --no-deps "git+https://${MY_GITHUB_USERNAME}:${BQ_IMPACTS_GITHUB_TOKEN}@github.com/BiodiversiteQuebec/bq_impact_indicators.git@demo/all-indicators-fixed"
```


### Running the project
Open a terminal in the root of the project. Run those commands :


1. To make sure you are in the virtual environment with the correct dependencies run:
```
source .venv/bin/activate

```

2. Now start the Fast API server
```
fastapi dev app/main.py
```

---

## Déploiement avec Docker

### 1. Configuration des variables d'environnement
Copiez le modèle d'environnement et renseignez vos identifiants :
```bash
cp .env.example .env
```

### 2. Déploiement rapide (via Makefile)
- **Construire l'image :**
  ```bash
  make build
  ```
- **Démarrer en arrière-plan (mode déploiement) :**
  ```bash
  make up
  ```
- **Consulter les logs :**
  ```bash
  make logs
  ```
- **Arrêter le conteneur :**
  ```bash
  make down
  ```
- **Mode développement (avec montage de code et rechargement à chaud) :**
  ```bash
  make dev
  ```

### 3. Déploiement Staging / Production
- **Staging :**
  ```bash
  make build-staging
  make start-staging
  ```
- **Production :**
  ```bash
  make build-production
  make start-production
  ```

L'API est accessible par défaut sur `http://localhost:8042` (ou le port configuré dans `PORT`), et l'état de santé est vérifiable sur `http://localhost:8042/health`.
