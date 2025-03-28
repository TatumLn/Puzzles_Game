# TP_1 : Puzzle Game (8-Puzzle & 15-Puzzle)

Bienvenue sur le projet **LOL Puzzle** ! Ce jeu est développé en Python avec Pygame et peut être exécuté dans un environnement Docker de maniere simple et fiable.<br>a - Choisissez entre le puzzle 3x3 ou 4x4.<br>b - Jouer : deplacez les tuiles pour résoudre les puzzles.<br>c - AI : Resoudre le puzzle automatiquement:<br>Pour la fonctionnalité de résolution automatique du N-puzzle, nous avons implémenté un algorithme heuristique basé sur les concepts suivants :
#### Distance de Manhattan :
Elle calcule la distance minimale entre la position actuelle d'une tuile et sa position cible en ne permettant que des déplacements horizontaux ou verticaux.
#### Conflits linéaires :
Une pénalité est ajoutée lorsque deux tuiles sont dans la même ligne ou colonne mais dans le mauvais ordre, augmentant ainsi le coût de déplacement.
#### Heuristiques :
utilisées avec l'algorithme A* pour guider efficacement la recherche de la solution optimale. Cela permet de résoudre le puzzle de manière rapide et précise, même pour des tailles plus grandes.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :
- [Docker](https://www.docker.com/)
- [Git](https://git-scm.com/)
- [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)

### 1. Cloner le dépôt
Utilisez la commande suivante pour cloner ce dépôt sur votre machine :
```bash
git clone https://github.com/TatumLn/Puzzles_Game.git
cd Puzzles_Game
```

### 2. Étapes pour lancer le projet 
i   - Construisez limage Docker
```bash
docker build -t puzzle-game:1.0 .
```
ii  - Lancer le conteneur (02 choix possible)
#### Avec docker run
```bash
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix puzzle-game:1.0
```
#### Avec docker compose
```bash
docker compose up
```

# TP_2 : Classification et Clustering

### 3. Lancer les fichiers .ipynb dans le dossier TP_2 

## Prérequis:
- [Google Colab](https://www.docker.com/)
- [Jupyter Notebook](https://jupyter.org/try/)

### Les Fichiers:
- **Fichier `iris.ipynb`** : Présent dans le dossier `TP_2` Classification - Etude du dataset Iris.
- **Fichier `instat.ipynb`** : Présent dans le dossier `TP_2` Clustering - Données Instat.

# TP_3 : Computer Vision

### Les Fichiers:
- **Fichier ``*AutoEncoder.ipynb* : TP de groupe sur l'AutoEncoder. 
- **Fichier ``*nom.ipynb* : TP individuel. 

## Contributeurs
- [TatumLn](https://github.com/TatumLn): Front-End && OPS & Game-Logic
- [Devkalix](https://github.com/Devkalix): Front-End & Game-Logic
- [RatsirofoFenosoa-Git](https://github.com/RatsirofoFenosoa-Git): Back-End & Game-Logic
- [toby7431](https://github.com/toby7431): Back-End & Game-Logic
- [DADDYB0Y](https://github.com/DADDYB0Y): Full-Stack & Game-Logic
