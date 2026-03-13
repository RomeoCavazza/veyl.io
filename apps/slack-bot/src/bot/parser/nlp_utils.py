"""
Utilitaires NLP simplifiés pour Revolver.bot.
Version sans dépendances lourdes.
"""

import re
import logging
from typing import Dict, Any, List
from collections import Counter

logger = logging.getLogger(__name__)

def extract_brief_sections(text: str) -> Dict[str, Any]:
    """Extrait les sections d'un brief à partir du texte - refactorisé"""
    sections = _initialize_sections()

    try:
        # Étape 1: Parsing du texte en sections
        parsed_sections = _parse_section_content(text)

        # Étape 2: Extraction du contenu de chaque section
        for section_name, content in parsed_sections.items():
            sections[section_name] = _extract_section_content(section_name, content)

        # Étape 3: Définition des valeurs par défaut
        _set_default_values(sections)

        return sections

    except Exception as e:
        return _handle_extraction_error(e, sections)

def _initialize_sections() -> Dict[str, Any]:
    """Initialise la structure des sections"""
    return {
        "titre": "",
        "problème": "",
        "objectifs": [],
        "kpis": []
    }

def _parse_section_content(text: str) -> Dict[str, str]:
    """Parse le texte pour extraire les sections par titres en majuscules"""
    sections = {}
    current_section = None
    current_content = []

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Détecte les titres de section (en majuscules)
        if line.isupper() and len(line) > 3:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()

            current_section = line.lower()
            current_content = []
        else:
            current_content.append(line)

    # Traite la dernière section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections

def _extract_section_content(section_name: str, content: str) -> Any:
    """Extrait le contenu d'une section selon son type"""
    if section_name in ["objectifs", "kpis"]:
        return [
            item.strip()
            for item in content.split(';')
            if item.strip()
        ]
    else:
        return content

def _set_default_values(sections: Dict[str, Any]):
    """Définit les valeurs par défaut pour les sections manquantes"""
    defaults = {
        "titre": "Brief extrait automatiquement",
        "problème": "Problème non précisé",
        "objectifs": ["Objectif non précisé"],
        "kpis": ["KPI non identifié"]
    }

    for key, default_value in defaults.items():
        if not sections[key]:
            sections[key] = default_value

def _handle_extraction_error(error: Exception, sections: Dict[str, Any]) -> Dict[str, Any]:
    """Gère les erreurs d'extraction et retourne les sections par défaut"""
    logger.error(f"[nlp_utils] Erreur lors de l'extraction des sections : {error}")
    return sections

def extract_keywords(text: str, n: int = 10) -> List[str]:
    """Extrait les mots-clés les plus pertinents du texte.
    
    Args:
        text: Le texte à analyser
        n: Nombre de mots-clés à extraire
        
    Returns:
        Liste des mots-clés extraits
    """
    # Version simplifiée sans spacy
    # Normalise le texte
    text = normalize_text(text.lower())
    
    # Liste de mots vides français
    stop_words = {
        'le', 'la', 'les', 'un', 'une', 'des', 'ce', 'ces', 'cette', 'de', 'du', 'des',
        'et', 'ou', 'mais', 'donc', 'car', 'ni', 'or', 'avec', 'sans', 'pour', 'par',
        'dans', 'sur', 'sous', 'entre', 'chez', 'vers', 'depuis', 'jusqu', 'pendant',
        'avant', 'après', 'dès', 'en', 'y', 'à', 'au', 'aux', 'se', 'sa', 'ses', 'son',
        'sa', 'ses', 'notre', 'votre', 'leur', 'leurs', 'mon', 'ma', 'mes', 'ton', 'ta',
        'tes', 'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te',
        'lui', 'leur', 'moi', 'toi', 'soi', 'qui', 'que', 'quoi', 'où', 'quand',
        'comment', 'pourquoi', 'combien', 'quel', 'quelle', 'quels', 'quelles'
    }
    
    # Extrait les mots
    words = re.findall(r'\b\w+\b', text)
    
    # Filtre les mots vides et les mots courts
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Compte et tri des mots-clés
    keyword_counts = Counter(keywords)
    
    return [word for word, _ in keyword_counts.most_common(n)]

def detect_language(text: str) -> str:
    """Détecte la langue du texte (version simplifiée).
    
    Args:
        text: Le texte à analyser
        
    Returns:
        Code de la langue détectée (fr, en, etc.)
    """
    # Version simplifiée basée sur les caractères
    text = text.lower()
    
    # Détection basique
    french_chars = set('àâäéèêëïîôöùûüÿç')
    english_chars = set('abcdefghijklmnopqrstuvwxyz')
    
    french_count = sum(1 for char in text if char in french_chars)
    english_count = sum(1 for char in text if char in english_chars)
    
    if french_count > english_count:
        return 'fr'
    else:
        return 'en'

def normalize_text(text: str) -> str:
    """Normalise le texte pour l'analyse.
    
    Args:
        text: Texte à normaliser
        
    Returns:
        Texte normalisé
    """
    # Supprime les caractères spéciaux
    text = re.sub(r'[^\w\s\-\']', ' ', text)
    
    # Remplace les espaces multiples par un seul
    text = re.sub(r'\s+', ' ', text)
    
    # Supprime les espaces en début/fin
    return text.strip()

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extrait les entités nommées du texte (version simplifiée).
    
    Args:
        text: Le texte à analyser
        
    Returns:
        Dictionnaire des entités par type
    """
    # Version simplifiée basée sur les regex
    entities = {
        'PERSON': [],
        'ORG': [],
        'LOC': [],
        'DATE': []
    }
    
    # Détection des dates
    date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    entities['DATE'] = re.findall(date_pattern, text)
    
    # Détection des organisations (mots en majuscules)
    org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    entities['ORG'] = re.findall(org_pattern, text)
    
    return entities

def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Génère un résumé du texte (version simplifiée).
    
    Args:
        text: Le texte à résumer
        max_sentences: Nombre maximum de phrases dans le résumé
        
    Returns:
        Le résumé généré
    """
    # Découpe en phrases
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return ". ".join(sentences)
    
    # Prend les premières phrases
    return ". ".join(sentences[:max_sentences])
