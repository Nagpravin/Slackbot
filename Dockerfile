
# FROM python:3.10-slim

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 3000

# ENV PYTHONUNBUFFERED=1

# CMD ["python", "app.py"]

FROM python:3.10-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install only needed system deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 3000
ENV PORT=3000

CMD ["python", "app.py"]
