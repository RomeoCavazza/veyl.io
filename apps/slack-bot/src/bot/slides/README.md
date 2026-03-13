# Module de génération de slides PowerPoint

Ce module permet de générer des présentations PowerPoint de manière programmatique.

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```python
from src.bot.slides import SlideBuilder

# Création d'une présentation
builder = SlideBuilder()

# Slide de titre
builder.add_title_slide(
    title="Ma présentation",
    subtitle="Un sous-titre"
)

# Slide de contenu
builder.add_content_slide(
    title="Points clés",
    points=[
        "Premier point",
        "Deuxième point",
        "Troisième point"
    ]
)

# Slide avec graphique
data = {
    "labels": ["A", "B", "C"],
    "values": [1, 2, 3]
}
builder.add_chart_slide(
    title="Statistiques",
    data=data,
    chart_type="bar"  # "bar", "column", "line", "pie"
)

# Slide avec image
builder.add_image_slide(
    title="Une image",
    image_path="chemin/vers/image.png"
)

# Sauvegarde
builder.save("presentation.pptx")
```

## Types de slides disponibles

1. **TitleSlide** : Slide de titre avec sous-titre optionnel
2. **ContentSlide** : Slide avec titre et points à puces
3. **ChartSlide** : Slide avec titre et graphique
4. **ImageSlide** : Slide avec titre et image

## Templates

Le module utilise un système de templates pour personnaliser l'apparence des slides.

### Template par défaut

Le template par défaut (`default.pptx`) est fourni avec le module et définit :
- Les mises en page standard
- Les polices et tailles de texte
- Les couleurs du thème

### Templates personnalisés

Pour créer un template personnalisé :
1. Créez un fichier `.pptx` dans le dossier `templates`
2. Ajoutez un fichier `.json` avec la configuration du template
3. Utilisez le template : `SlideBuilder(template="mon_template")`

## Formatage du texte

Le module supporte un formatage markdown basique :
- `**texte**` : Gras
- `*texte*` : Italique
- `_texte_` : Souligné

## Graphiques

Types de graphiques supportés :
- `bar` : Graphique à barres
- `column` : Graphique à colonnes
- `line` : Graphique en ligne
- `pie` : Graphique en camembert

## Images

Les images sont automatiquement :
- Redimensionnées pour s'adapter à la slide
- Centrées dans la slide
- Optimisées pour la qualité 