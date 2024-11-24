# Puzzle Game (8-Puzzle & 15-Puzzle)

Bienvenue dans le projet **Puzzle Game** ! Ce jeu est développé en Python avec Pygame et peut être exécuté dans un environnement Docker de maniere simple et fiable.<br>a - Choisissez entre le puzzle 3x3 ou 4x4.<br>b - Jouer : deplacez les tuiles pour resoudre les puzzles.<br>c - AI : Resoudre le puzzle automatiquement.

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
iii - Pour windows 
```bash

```

## Contributeurs
- [TatumLn](https://github.com/TatumLn): Front-End && OPS
- [Devkalix](https://github.com/Devkalix): Front-End
- [RatsirofoFenosoa-Git](https://github.com/RatsirofoFenosoa-Git): Back-End
- [toby7431](https://github.com/toby7431): Back-End
- [DADDYB0Y](https://github.com/DADDYB0Y): Full-Stack
