#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
import soundfile as sf
import numpy as np

def split_audio(input_file, segment_length=5*60):
    """
    Découpe un fichier audio en segments de la longueur spécifiée (en secondes).
    
    Args:
        input_file: Chemin vers le fichier audio d'entrée
        segment_length: Longueur de chaque segment en secondes
                        (par défaut: 5 minutes)
    
    Returns:
        Une liste de chemins vers les fichiers temporaires créés
    """
    print(f"Chargement du fichier audio: {input_file}")
    try:
        # Obtenir les informations du fichier sans charger toutes les données
        info = sf.info(input_file)
        sample_rate = info.samplerate
        total_samples = info.frames
        duration = info.duration
        channels = info.channels
    except Exception as e:
        print(f"Erreur lors de la lecture des informations du fichier audio: {e}")
        return []
    
    # Calculer la taille de chaque segment en échantillons
    segment_samples = int(segment_length * sample_rate)
    
    segments = []
    temp_dir = tempfile.mkdtemp()
    
    # Création du nom de base pour les fichiers temporaires
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    
    print(f"Durée totale du fichier: {duration:.2f} secondes ({duration/60:.2f} minutes)")
    print(f"Découpage en segments de {segment_length} secondes...")
    
    # Ouvrir le fichier en mode lecture
    with sf.SoundFile(input_file, 'r') as f:
        segment_count = 0
        
        # Traiter le fichier par blocs pour économiser la mémoire
        for i in range(0, total_samples, segment_samples):
            segment_count += 1
            # Calculer le nombre d'échantillons à lire (peut être moins pour le dernier segment)
            block_size = min(segment_samples, total_samples - i)
            
            # Lire le bloc d'échantillons
            data = f.read(block_size)
            
            # Créer le fichier pour ce segment
            segment_file = os.path.join(temp_dir, f"{base_filename}_segment_{segment_count}.flac")
            
            # Écrire les données dans le nouveau fichier
            sf.write(segment_file, data, sample_rate)
            
            segment_duration = block_size / sample_rate
            print(f"Segment créé: {segment_file} ({segment_duration:.2f} secondes)")
            
            segments.append(segment_file)
    
    return segments

def run_inference(segment_files, output_folder):
    """
    Exécute la commande d'inférence avec tous les segments en une seule fois.
    
    Args:
        segment_files: Liste des segments à traiter
        output_folder: Dossier de sortie pour les résultats
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Construction de la commande d'inférence avec tous les segments à la fois et les paramètres supplémentaires
    cmd = ["python", "inference_modifier.py", "--input_audio"] + segment_files + [
        "--output_folder", output_folder,
        "--large_gpu",
        "--only_vocals",
        "--overlap_large", "0.7",
        "--overlap_small", "0.6",
        "--chunk_size", "2000000"
    ]
    
    print(f"Exécution de la commande: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Traitement terminé avec succès. Résultats enregistrés dans {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande d'inférence: {e}")

def main():
    parser = argparse.ArgumentParser(description="Découpe un fichier audio FLAC et exécute l'inférence sur chaque segment")
    parser.add_argument("--input_audio", required=True, help="Fichier audio FLAC d'entrée")
    parser.add_argument("--output_folder", default="./results", help="Dossier pour les résultats (par défaut: ./results)")
    parser.add_argument("--segment_length", type=int, default=5, help="Longueur de chaque segment en minutes (par défaut: 5)")
    
    args = parser.parse_args()
    
    # Conversion de la longueur du segment en secondes
    segment_length_sec = args.segment_length * 60
    
    # Découpage du fichier audio
    segment_files = split_audio(args.input_audio, segment_length_sec)
    
    if segment_files:
        # Exécution de l'inférence sur les segments
        run_inference(segment_files, args.output_folder)
    else:
        print("Aucun segment n'a été créé. Vérifiez le fichier d'entrée.")

if __name__ == "__main__":
    main()
