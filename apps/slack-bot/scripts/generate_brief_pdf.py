#!/usr/bin/env python3
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_pdf(input_path: str, output_path: str) -> None:
    """Génère un PDF à partir d'un fichier texte."""
    # Lecture du contenu
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Création du PDF
    c = canvas.Canvas(output_path, pagesize=letter)
    y = 750  # Position verticale initiale
    
    # Écriture du contenu
    for line in content.split('\n'):
        if line.strip():
            c.drawString(50, y, line)
            y -= 15  # Espacement entre les lignes
        else:
            y -= 20  # Espacement plus grand pour les lignes vides
            
        if y < 50:  # Nouvelle page si on arrive en bas
            c.showPage()
            y = 750
    
    c.save()

def main():
    parser = argparse.ArgumentParser(description='Génère un PDF à partir d\'un fichier texte')
    parser.add_argument('--input', required=True, help='Fichier texte d\'entrée')
    parser.add_argument('--output', required=True, help='Fichier PDF de sortie')
    
    args = parser.parse_args()
    
    # Création du répertoire de sortie si nécessaire
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    generate_pdf(args.input, args.output)

if __name__ == '__main__':
    main() 