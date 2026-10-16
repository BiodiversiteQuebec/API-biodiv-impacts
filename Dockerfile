FROM python:3.12

WORKDIR /app

# Accept build arguments for private git repository access
ARG MY_GITHUB_USERNAME
ARG BQ_IMPACTS_GITHUB_TOKEN

# Set environment variables for pip requirements expansion
ENV MY_GITHUB_USERNAME=${MY_GITHUB_USERNAME}
ENV BQ_IMPACTS_GITHUB_TOKEN=${BQ_IMPACTS_GITHUB_TOKEN}

# Install dependencies in a cached layer
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Clear secret build token so it does not persist in the final container image
ENV BQ_IMPACTS_GITHUB_TOKEN=""

# Copy application source code
COPY . ./

# Expose default port
EXPOSE 8080

# Run FastAPI production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
