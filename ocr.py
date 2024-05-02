import json
import requests
from threading import Thread
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Fonction pour faire la requête OCR sur une seule image et stocker le résultat dans un index spécifique
def process_image(img, results, index):
    try:
        with open(img, "rb") as file:
            r = requests.post("https://api.mathpix.com/v3/text",
                files={"file": file},
                data={"options_json": json.dumps({"formats": ["text"]})},
                headers={
                    "app_id": os.getenv("MATHPIX_app_id"),
                    "app_key": os.getenv("MATHPIX_API_KEY"),
                }
            )
            response = r.json()
            results[index] = response.get("text")
    except Exception as e:
        print(f"Error processing {img}: {e}")
        results[index] = f"Error: {e}"

# Fonction principale pour traiter les images en utilisant des threads
def ocr_files(imgs):
    threads = []
    results = [None] * len(imgs)  # Créer une liste pour stocker les résultats

    # Créer et démarrer un thread pour chaque image
    for i, img in enumerate(imgs):
        thread = Thread(target=process_image, args=(img, results, i))
        threads.append(thread)
        thread.start()

    # Attendre que tous les threads soient terminés
    for thread in threads:
        thread.join()

    # Joindre tous les résultats en une seule chaîne, en conservant l'ordre
    return " ".join(results)