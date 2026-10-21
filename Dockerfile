FROM python:3.12

WORKDIR /app

# 1. Install system dependencies: git and git-lfs
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    git-lfs \
    && git lfs install \
    && rm -rf /var/lib/apt/lists/*

# 2. Build arguments for private GitHub repository access
ARG MY_GITHUB_USERNAME
ARG BQ_IMPACTS_GITHUB_TOKEN

# 3. Clone with Git LFS, install package, and guarantee all data files are in site-packages
RUN git clone --depth 1 -b demo/all-indicators-fixed \
    https://${MY_GITHUB_USERNAME}:${BQ_IMPACTS_GITHUB_TOKEN}@github.com/BiodiversiteQuebec/bq_impact_indicators.git /tmp/bq \
    && cd /tmp/bq \
    && git lfs pull \
    && pip install --no-cache-dir . \
    && cd /app \
    && python -c "import bq_impact_indicators, os, shutil; dst = os.path.join(os.path.dirname(bq_impact_indicators.__file__), 'data'); shutil.copytree('/tmp/bq/bq_impact_indicators/data', dst, dirs_exist_ok=True)" \
    && rm -rf /tmp/bq

# 4. Install API server dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Clear sensitive build tokens
ENV BQ_IMPACTS_GITHUB_TOKEN=""
ENV MY_GITHUB_USERNAME=""

# 6. Copy application code
COPY . ./

EXPOSE 8042

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8042"]
