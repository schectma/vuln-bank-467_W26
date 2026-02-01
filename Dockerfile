FROM python:3.9-slim

# Install PostgreSQL client
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    zstd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
# RUN curl -fsSL https://ollama.com/install.sh | sh

# Pre-download model during build
# RUN ollama serve & \
#     sleep 5 && \
#     ollama pull llama3.2:latest && \
#     pkill ollama

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p static/uploads templates

COPY . .

# Ensure uploads directory exists and has proper permissions
RUN chmod 777 static/uploads

EXPOSE 5000

CMD ["python", "app.py"]
# Start both Ollama and Flask
# CMD ["sh", "-c", "ollama serve & sleep 5 && python app.py"]