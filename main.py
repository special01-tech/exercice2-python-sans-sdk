import base64
import json
import os
import sys
import time

import requests

BASE_URL = "https://api.rodiumai.io/v1"


# 1) Récupérer la clé API
def charger_cle():
    """Cherche RODIUMAI_API_KEY dans l'environnement, sinon dans un fichier .env
    (dans le dossier du script, ou dans le dossier au-dessus)."""
    cle = os.environ.get("RODIUMAI_API_KEY")
    if cle:
        return cle.strip()
    dossier = os.path.dirname(os.path.abspath(__file__))
    for chemin in (os.path.join(dossier, ".env"), os.path.join(dossier, "..", ".env")):
        if os.path.isfile(chemin):
            with open(chemin, encoding="utf-8-sig") as f:
                for ligne in f:
                    ligne = ligne.strip().replace("export ", "", 1)
                    if ligne.startswith("RODIUMAI_API_KEY="):
                        return ligne.split("=", 1)[1].strip().strip('"').strip("'")
    return None


API_KEY = charger_cle()
if not API_KEY:
    sys.exit("Clé introuvable : vérifiez que le fichier .env contient RODIUMAI_API_KEY=rd_sk_...")

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


# 2) Fonction commune : envoie la requête, mesure le temps, gère les erreurs
def appeler(chemin, corps, timeout=120):
    debut = time.perf_counter()
    try:
        r = requests.post(BASE_URL + chemin, headers=HEADERS, json=corps, timeout=timeout)
    except requests.exceptions.RequestException as e:
        print("Erreur réseau ou timeout :", e)
        return None
    print(f"[HTTP {r.status_code}] en {time.perf_counter() - debut:.2f} s")
    try:
        data = r.json()
    except ValueError:
        print(r.text)
        return None
    if r.status_code != 200:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return None
    return data


# 3) Les trois étapes
def etape_chat():
    data = appeler("/chat/completions", {
        "model": "anthropic/claude-haiku-4-5-20251001",
        "messages": [{"role": "user", "content": "Écris une accroche pour un restaurant de quartier."}],
        "max_tokens": 300,
    })
    if data:
        print(data["choices"][0]["message"]["content"])
        print("Coût (RODI) :", data.get("cost_rodi"))


def etape_image():
    data = appeler("/images/generations", {
        "model": "google/gemini-3.1-flash-lite-image",
        "prompt": "Un plat appétissant dans un restaurant de quartier, lumière naturelle",
        "n": 1,
        "size": "1024x1024",
        "quality": "low",
    }, timeout=180)
    if data:
        # L'image arrive en base64 (du texte) : on la décode pour créer le fichier
        with open("image.png", "wb") as f:
            f.write(base64.b64decode(data["data"][0]["b64_json"]))
        print("Image enregistrée : image.png")
        print("Coût (RODI) :", data.get("cost_rodi"))


def etape_video():
    data = appeler("/videos/generations", {
        "model": "google/veo-3.1-fast",
        "prompt": "Un cuisinier prépare un plat, gros plan, ambiance chaleureuse",
        "duration_seconds": 8,
        "aspect_ratio": "9:16",
    }, timeout=600)  # la vidéo peut prendre plusieurs minutes
    if data:
        item = data["data"][0]
        if item.get("b64_json"):
            contenu = base64.b64decode(item["b64_json"])
        else:
            contenu = requests.get(item["url"], timeout=120).content
        with open("video.mp4", "wb") as f:
            f.write(contenu)
        print("Vidéo enregistrée : video.mp4")
        print("Coût (RODI) :", data.get("cost_rodi"))


# 4) Le menu : précédent / rester / suivant
ETAPES = [("Chat", etape_chat), ("Image", etape_image), ("Vidéo", etape_video)]

i = 0
while i < len(ETAPES):
    nom, fonction = ETAPES[i]
    print(f"\n=== Étape {i + 1}/{len(ETAPES)} : {nom} ===")
    fonction()
    choix = ""
    while choix not in ("p", "r", "s"):
        choix = input("\n(p) précédent, (r) rester, (s) suivant ? ").strip().lower()
    if choix == "p":
        i = max(0, i - 1)
    elif choix == "s":
        i += 1
    # "r" : on reste sur la même étape et on la relance
print("\nTerminé.")