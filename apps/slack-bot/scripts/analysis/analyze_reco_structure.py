#!/usr/bin/env python3
"""
Script d'analyse des structures de recommandations
Analyse les exemples RECO pour comprendre les patterns
"""

import os
import json
import PyPDF2
from pathlib import Path
from typing import Dict, List, Any
import re

class RecoAnalyzer:
    """Analyseur de structures de recommandations"""
    
    def __init__(self, reco_dir: str = "examples/RECO"):
        self.reco_dir = Path(reco_dir)
        self.analysis_results = {}
    
    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extrait le texte d'un PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Erreur lors de l'extraction de {pdf_path}: {e}")
            return ""
    
    def analyze_pdf_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """Analyse la structure d'un PDF de recommandation"""
        print(f"🔍 Analyse de {pdf_path.name}...")
        
        text = self.extract_pdf_text(pdf_path)
        if not text:
            return {"error": "Impossible d'extraire le texte"}
        
        # Analyse de la structure
        analysis = {
            "filename": pdf_path.name,
            "size_mb": pdf_path.stat().st_size / (1024 * 1024),
            "total_pages": len(text.split('\n')) // 50,  # Estimation
            "sections": self.extract_sections(text),
            "patterns": self.detect_patterns(text),
            "key_elements": self.extract_key_elements(text)
        }
        
        return analysis
    
    def extract_sections(self, text: str) -> List[str]:
        """Extrait les sections principales"""
        # Patterns pour détecter les sections
        section_patterns = [
            r'(?:^|\n)([A-Z][A-Z\s&]+)(?:\n|$)',
            r'(?:^|\n)(\d+\.\s*[A-Z][A-Za-z\s]+)(?:\n|$)',
            r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\n|$)'
        ]
        
        sections = []
        for pattern in section_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            sections.extend([m.strip() for m in matches if len(m.strip()) > 3])
        
        return list(set(sections))[:20]  # Top 20 sections
    
    def detect_patterns(self, text: str) -> Dict[str, Any]:
        """Détecte les patterns récurrents"""
        patterns = {
            "has_budget": "budget" in text.lower() or "€" in text or "$" in text,
            "has_timeline": any(word in text.lower() for word in ["timeline", "planning", "échéance", "deadline"]),
            "has_competitors": any(word in text.lower() for word in ["concurrent", "competitor", "benchmark"]),
            "has_trends": any(word in text.lower() for word in ["tendance", "trend", "culturel", "sociétal"]),
            "has_kpis": any(word in text.lower() for word in ["kpi", "indicateur", "métrique", "performance"]),
            "has_insights": any(word in text.lower() for word in ["insight", "analyse", "observation"]),
            "slide_count": len(re.findall(r'slide|diapositive', text.lower())),
            "image_references": len(re.findall(r'image|photo|visuel', text.lower()))
        }
        return patterns
    
    def extract_key_elements(self, text: str) -> Dict[str, List[str]]:
        """Extrait les éléments clés"""
        elements = {
            "brands": re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text)[:10],
            "numbers": re.findall(r'\d+(?:\.\d+)?%?', text)[:10],
            "dates": re.findall(r'\d{4}', text)[:10],
            "urls": re.findall(r'https?://[^\s]+', text)
        }
        return elements
    
    def analyze_all_recos(self) -> Dict[str, Any]:
        """Analyse tous les fichiers de recommandation"""
        print("🚀 Début de l'analyse des recommandations...")
        
        pdf_files = list(self.reco_dir.glob("*.pdf"))
        pptx_files = list(self.reco_dir.glob("*.pptx"))
        
        print(f"📁 Trouvé {len(pdf_files)} PDFs et {len(pptx_files)} PPTXs")
        
        # Analyse des PDFs
        for pdf_file in pdf_files:
            if "RECO" in pdf_file.name or "recommandation" in pdf_file.name.lower():
                self.analysis_results[pdf_file.name] = self.analyze_pdf_structure(pdf_file)
        
        # Résumé global
        summary = self.generate_summary()
        
        return {
            "files_analyzed": len(self.analysis_results),
            "summary": summary,
            "detailed_analysis": self.analysis_results
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Génère un résumé des patterns détectés"""
        if not self.analysis_results:
            return {}
        
        # Compilation des patterns
        all_patterns = []
        all_sections = []
        
        for analysis in self.analysis_results.values():
            if "patterns" in analysis:
                all_patterns.append(analysis["patterns"])
            if "sections" in analysis:
                all_sections.extend(analysis["sections"])
        
        # Patterns les plus fréquents
        common_patterns = {}
        if all_patterns:
            for key in all_patterns[0].keys():
                if isinstance(all_patterns[0][key], bool):
                    common_patterns[key] = sum(p.get(key, False) for p in all_patterns)
        
        # Sections les plus fréquentes
        section_counts = {}
        for section in all_sections:
            section_counts[section] = section_counts.get(section, 0) + 1
        
        return {
            "common_patterns": common_patterns,
            "top_sections": sorted(section_counts.items(), key=lambda x: x[1], reverse=True)[:15],
            "total_files": len(self.analysis_results)
        }
    
    def save_analysis(self, output_file: str = "reco_analysis_results.json"):
        """Sauvegarde les résultats d'analyse"""
        results = self.analyze_all_recos()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés dans {output_file}")
        return results

def main():
    """Fonction principale"""
    analyzer = RecoAnalyzer()
    results = analyzer.save_analysis()
    
    # Affichage du résumé
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DE L'ANALYSE")
    print("="*50)
    
    summary = results.get("summary", {})
    print(f"📁 Fichiers analysés: {summary.get('total_files', 0)}")
    
    print("\n🔍 Patterns détectés:")
    for pattern, count in summary.get("common_patterns", {}).items():
        print(f"  - {pattern}: {count}/{summary.get('total_files', 0)}")
    
    print("\n📋 Sections les plus fréquentes:")
    for section, count in summary.get("top_sections", [])[:10]:
        print(f"  - {section}: {count} occurrences")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 