FROM python:3.12
WORKDIR /app
COPY requirements.txt ./

# Accept build arguments
ARG GITHUB_USERNAME
ARG BQ_IMPACTS_GITHUB_TOKEN

# Set them as environment variables
ENV GITHUB_USERNAME=${GITHUB_USERNAME}
ENV BQ_IMPACTS_GITHUB_TOKEN=${BQ_IMPACTS_GITHUB_TOKEN}

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
