#!/usr/bin/env python3
import argparse
import os
import subprocess
import tempfile
from pydub import AudioSegment

def split_audio(input_file, segment_length=5*60*1000):
    """
    Découpe un fichier audio en segments de la longueur spécifiée (en ms).
    
    Args:
        input_file: Chemin vers le fichier audio d'entrée
        segment_length: Longueur de chaque segment en millisecondes
                        (par défaut: 5 minutes)
    
    Returns:
        Une liste de chemins vers les fichiers temporaires créés
    """
    print(f"Chargement du fichier audio: {input_file}")
    try:
        audio = AudioSegment.from_file(input_file, format="flac")
    except Exception as e:
        print(f"Erreur lors du chargement du fichier audio: {e}")
        return []

    total_length = len(audio)
    segments = []
    temp_dir = tempfile.mkdtemp()
    
    # Création du nom de base pour les fichiers temporaires
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    
    # Découpage du fichier audio
    for i in range(0, total_length, segment_length):
        segment = audio[i:i+segment_length]
        segment_file = os.path.join(temp_dir, f"{base_filename}_segment_{i//segment_length + 1}.flac")
        segment.export(segment_file, format="flac")
        segments.append(segment_file)
        print(f"Segment créé: {segment_file} ({len(segment)/1000:.2f} secondes)")
    
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
    
    # Construction de la commande d'inférence avec tous les segments à la fois
    cmd = ["python", "inference.py", "--input_audio"] + segment_files + ["--output_folder", output_folder]
    
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
    
    # Conversion de la longueur du segment en millisecondes
    segment_length_ms = args.segment_length * 60 * 1000
    
    # Découpage du fichier audio
    segment_files = split_audio(args.input_audio, segment_length_ms)
    
    if segment_files:
        # Exécution de l'inférence sur les segments
        run_inference(segment_files, args.output_folder)
    else:
        print("Aucun segment n'a été créé. Vérifiez le fichier d'entrée.")

if __name__ == "__main__":
    main()