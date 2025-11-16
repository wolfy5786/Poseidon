# ---- Base Image ----
FROM python:3.10-slim

# ---- Install Node & Newman ----
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g newman && \
    apt-get clean

# ---- Set Working Directory ----
WORKDIR /app

# ---- Copy Requirements ----
COPY core/requirements.txt .

# ---- Install Python Dependencies ----
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy source code to container Code ----
COPY core/ ./core/ 
COPY config/ ./config/
COPY interface/ ./interface/
# ---- Default Entrypoint ----
CMD ["python", "core/orchestrator/orchestrator.py"]
