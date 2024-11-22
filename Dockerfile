# image python
FROM python:3.13.0

# dependances 
RUN apt-get update && apt-get install -y \
    libx11-dev libxext-dev libxrender-dev libxrandr-dev libxcursor-dev && \
    apt-get clean

# repetoire de travail
WORKDIR /app

# copie des fichiers necessaires dans le conteneur
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#Lancer le jeu
CMD ["python", "main.py"]
