# Exercice 2 : script Python sans SDK (RodiumAi)

Script en ligne de commande qui appelle l'API RodiumAi avec la bibliothèque
`requests`, sans SDK : chat, génération d'image, génération de vidéo.
Après chaque étape, on choisit : `p` (précédent), `r` (rester), `s` (suivant).

## Prérequis
- Python 3
- Une clé API RodiumAi

## Installation
pip install requests

## Configuration
Créer un fichier `.env` à côté du script (ou dans le dossier au-dessus) :

RODIUMAI_API_KEY=rd_sk_votre_cle

La clé n'est jamais écrite dans le code ni envoyée sur GitHub.

## Lancement
python main.py

## Endpoints utilisés
- POST /v1/chat/completions
- POST /v1/images/generations (fichier image.png créé)
- POST /v1/videos/generations (fichier video.mp4 créé)

## Fonctionnement
Le temps de réponse et le coût en RODI sont affichés à chaque étape.
Les erreurs (401, 402, 404, timeout) sont affichées sans faire planter le script.