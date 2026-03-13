"""Script pour créer le template PowerPoint par défaut."""

from pptx import Presentation
from pptx.util import Inches, Pt
from pathlib import Path

def create_default_template():
    """Crée le template PowerPoint par défaut."""
    # Création du template
    prs = Presentation()

    # Slide de titre
    title_slide = prs.slide_layouts[0]
    title_slide.name = 'Title Slide'

    # Slide de contenu
    content_slide = prs.slide_layouts[1]
    content_slide.name = 'Content'

    # Slide avec graphique
    chart_slide = prs.slide_layouts[2]
    chart_slide.name = 'Chart'

    # Slide avec image
    picture_slide = prs.slide_layouts[3]
    picture_slide.name = 'Picture'

    # Création du dossier templates s'il n'existe pas
    templates_dir = Path('src/bot/slides/templates')
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Sauvegarde du template
    prs.save(templates_dir / 'default.pptx')
    print("Template créé avec succès !")

if __name__ == "__main__":
    create_default_template() 