from typing import Dict, Any, List
from pathlib import Path

def validate_pdf(file_path: str) -> bool:
    """Valide un fichier PDF.
    
    Args:
        file_path: Chemin vers le fichier PDF
        
    Returns:
        True si le fichier est valide
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False
        if path.suffix.lower() != ".pdf":
            return False
        # TODO: Ajouter plus de validations
        return True
    except Exception:
        return False

def validate_brief_content(content: Dict[str, Any]) -> List[str]:
    """Valide le contenu d'un brief.
    
    Args:
        content: Contenu du brief
        
    Returns:
        Liste des erreurs de validation
    """
    errors = []
    
    # Vérifie les champs requis
    required_fields = ["title", "problem", "objectives"]
    for field in required_fields:
        if field not in content:
            errors.append(f"Champ requis manquant : {field}")
            
    # Vérifie le format des champs
    if "objectives" in content and not isinstance(content["objectives"], list):
        errors.append("Les objectifs doivent être une liste")
        
    return errors
