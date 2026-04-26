FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for some python packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway provides the PORT environment variable
ENV PORT=8000
EXPOSE 8000

# main.py handles the PORT env variable correctly
CMD ["python", "main.py"]
