#!/usr/bin/env python3
"""
Analyse détaillée de la structure des slides Havana Club
Extrait les patterns spécifiques pour comprendre l'architecture des recommandations
"""

import PyPDF2
import re
from pathlib import Path
from typing import Dict, List, Any
import json

class HavanaSlidesAnalyzer:
    """Analyseur spécialisé pour les slides Havana Club"""
    
    def __init__(self):
        self.havana_pdf = Path("examples/RECO/RECO HAVANA CLUB.pdf")
        self.slide_structure = {}
        
    def extract_havana_content(self) -> str:
        """Extrait le contenu du PDF Havana Club"""
        try:
            with open(self.havana_pdf, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    text += f"\n=== PAGE {i+1} ===\n{page_text}\n"
                return text
        except Exception as e:
            print(f"Erreur lors de l'extraction: {e}")
            return ""
    
    def identify_slide_sections(self, text: str) -> Dict[str, Any]:
        """Identifie les sections de slides"""
        print("🔍 Identification des sections de slides...")
        
        # Patterns pour les titres de slides
        slide_patterns = [
            r'(?:^|\n)(\d+\.\s*[A-Z][A-Za-z\s]+)(?:\n|$)',
            r'(?:^|\n)([A-Z][A-Z\s]+)(?:\n|$)',
            r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\n|$)'
        ]
        
        sections = {}
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Détection de nouvelle section
            is_section_header = False
            for pattern in slide_patterns:
                if re.match(pattern, line):
                    # Sauvegarde de la section précédente
                    if current_section and current_content:
                        sections[current_section] = {
                            'content': '\n'.join(current_content),
                            'lines': len(current_content),
                            'keywords': self.extract_keywords('\n'.join(current_content))
                        }
                    
                    current_section = line
                    current_content = []
                    is_section_header = True
                    break
            
            if not is_section_header and current_section:
                current_content.append(line)
        
        # Dernière section
        if current_section and current_content:
            sections[current_section] = {
                'content': '\n'.join(current_content),
                'lines': len(current_content),
                'keywords': self.extract_keywords('\n'.join(current_content))
            }
        
        return sections
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés d'un texte"""
        # Mots-clés spécifiques aux recommandations
        keywords = []
        
        # Marques et concurrents
        brands = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text)
        keywords.extend([b for b in brands if len(b) > 2])
        
        # Chiffres et pourcentages
        numbers = re.findall(r'\d+(?:\.\d+)?%?', text)
        keywords.extend(numbers[:5])
        
        # Mots-clés stratégiques
        strategic_words = [
            'budget', 'timeline', 'trend', 'tendance', 'concurrent', 'benchmark',
            'kpi', 'insight', 'opportunité', 'threat', 'market', 'marché',
            'target', 'cible', 'positioning', 'positionnement', 'brand', 'marque'
        ]
        
        for word in strategic_words:
            if word in text.lower():
                keywords.append(word)
        
        return list(set(keywords))[:10]
    
    def analyze_slide_structure(self) -> Dict[str, Any]:
        """Analyse complète de la structure des slides"""
        print("🚀 Analyse de la structure des slides Havana Club...")
        
        text = self.extract_havana_content()
        if not text:
            return {"error": "Impossible d'extraire le contenu"}
        
        # Identification des sections
        sections = self.identify_slide_sections(text)
        
        # Analyse des patterns
        patterns = self.analyze_patterns(text)
        
        # Structure des 7 parties
        seven_parts = self.map_to_seven_parts(sections)
        
        analysis = {
            "filename": self.havana_pdf.name,
            "total_pages": len(text.split('=== PAGE')) - 1,
            "sections_found": len(sections),
            "sections": sections,
            "patterns": patterns,
            "seven_parts_mapping": seven_parts,
            "recommendations": self.generate_recommendations(sections, patterns)
        }
        
        return analysis
    
    def analyze_patterns(self, text: str) -> Dict[str, Any]:
        """Analyse les patterns récurrents"""
        patterns = {
            "has_brand_overview": any(word in text.lower() for word in ["brand overview", "vue d'ensemble", "marque"]),
            "has_state_of_play": any(word in text.lower() for word in ["state of play", "état", "marché", "concurrent"]),
            "has_cultural_trends": any(word in text.lower() for word in ["cultural", "culturel", "tendance"]),
            "has_tiktok_trends": "tiktok" in text.lower(),
            "has_societal_trends": any(word in text.lower() for word in ["societal", "sociétal", "société"]),
            "has_timeline": any(word in text.lower() for word in ["timeline", "planning", "échéance"]),
            "has_budget": any(word in text.lower() for word in ["budget", "€", "$", "coût"]),
            "slide_count": len(re.findall(r'slide|diapositive', text.lower())),
            "image_count": len(re.findall(r'image|photo|visuel', text.lower())),
            "chart_count": len(re.findall(r'graphique|chart|diagramme', text.lower()))
        }
        return patterns
    
    def map_to_seven_parts(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Mappe les sections aux 7 parties standard"""
        mapping = {
            "1. Brand Overview": [],
            "2. State of Play": [],
            "3. Idea #1. Cultural Trends": [],
            "4. Idea #2. TikTok Trends": [],
            "5. Idea #3. Societal Trends": [],
            "6. Timeline": [],
            "7. Budget": []
        }
        
        for section_name, section_data in sections.items():
            content = section_data.get('content', '').lower()
            
            # Mapping intelligent
            if any(word in content for word in ['brand', 'marque', 'overview', 'vue']):
                mapping["1. Brand Overview"].append(section_name)
            elif any(word in content for word in ['state', 'play', 'marché', 'concurrent', 'benchmark']):
                mapping["2. State of Play"].append(section_name)
            elif any(word in content for word in ['cultural', 'culturel', 'tendance']):
                mapping["3. Idea #1. Cultural Trends"].append(section_name)
            elif 'tiktok' in content:
                mapping["4. Idea #2. TikTok Trends"].append(section_name)
            elif any(word in content for word in ['societal', 'sociétal', 'société']):
                mapping["5. Idea #3. Societal Trends"].append(section_name)
            elif any(word in content for word in ['timeline', 'planning', 'échéance']):
                mapping["6. Timeline"].append(section_name)
            elif any(word in content for word in ['budget', '€', '$', 'coût']):
                mapping["7. Budget"].append(section_name)
        
        return mapping
    
    def generate_recommendations(self, sections: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Génère des recommandations pour améliorer la structure"""
        recommendations = []
        
        # Vérification des 7 parties
        seven_parts = self.map_to_seven_parts(sections)
        missing_parts = [part for part, mapped in seven_parts.items() if not mapped]
        
        if missing_parts:
            recommendations.append(f"Parties manquantes: {', '.join(missing_parts)}")
        
        # Recommandations sur les patterns
        if not patterns.get("has_brand_overview"):
            recommendations.append("Ajouter une section Brand Overview claire")
        
        if not patterns.get("has_state_of_play"):
            recommendations.append("Ajouter une section State of Play avec benchmark concurrentiel")
        
        if not patterns.get("has_cultural_trends"):
            recommendations.append("Développer les tendances culturelles")
        
        if not patterns.get("has_tiktok_trends"):
            recommendations.append("Inclure des tendances TikTok spécifiques")
        
        if not patterns.get("has_societal_trends"):
            recommendations.append("Ajouter des tendances sociétales")
        
        if not patterns.get("has_timeline"):
            recommendations.append("Inclure un timeline détaillé")
        
        if not patterns.get("has_budget"):
            recommendations.append("Détailler le budget et les coûts")
        
        return recommendations
    
    def save_analysis(self, output_file: str = "havana_slides_analysis.json"):
        """Sauvegarde l'analyse"""
        analysis = self.analyze_slide_structure()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Analyse sauvegardée dans {output_file}")
        return analysis

def main():
    """Fonction principale"""
    analyzer = HavanaSlidesAnalyzer()
    results = analyzer.save_analysis()
    
    # Affichage du résumé
    print("\n" + "="*60)
    print("📊 ANALYSE DÉTAILLÉE - HAVANA CLUB SLIDES")
    print("="*60)
    
    print(f"📁 Fichier analysé: {results.get('filename', 'N/A')}")
    print(f"📄 Pages totales: {results.get('total_pages', 0)}")
    print(f"📋 Sections trouvées: {results.get('sections_found', 0)}")
    
    print("\n🔍 Patterns détectés:")
    patterns = results.get('patterns', {})
    for pattern, value in patterns.items():
        if isinstance(value, bool):
            status = "✅" if value else "❌"
            print(f"  {status} {pattern}: {value}")
        else:
            print(f"  📊 {pattern}: {value}")
    
    print("\n📋 Mapping vers les 7 parties:")
    seven_parts = results.get('seven_parts_mapping', {})
    for part, mapped_sections in seven_parts.items():
        if mapped_sections:
            print(f"  ✅ {part}: {len(mapped_sections)} section(s)")
            for section in mapped_sections[:2]:  # Affiche les 2 premières
                print(f"    - {section}")
        else:
            print(f"  ❌ {part}: Aucune section mappée")
    
    print("\n💡 Recommandations:")
    recommendations = results.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main() 