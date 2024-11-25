# image python
FROM python:3.13.0-slim

# dependances 
RUN apt-get update && apt-get install -y \
    x11-apps\
    libx11-dev \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# repetoire de travail
WORKDIR /app

# copie des fichiers necessaires dans le conteneur
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie assets 
COPY assets/ ./assets/
COPY . .

#Lancer le jeu
CMD ["python", "main.py"]
