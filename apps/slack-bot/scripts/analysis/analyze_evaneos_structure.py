#!/usr/bin/env python3
"""
Analyse détaillée de la reco EVANEOS - Validation des patterns
"""
from src.bot.parser.pdf_parser import extract_text_from_pdf
import json

def analyze_evaneos_structure():
    """Analyse détaillée de la reco EVANEOS"""
    
    print("=== ANALYSE DÉTAILLÉE - EVANEOS ===")
    
    # Extraction du texte complet
    text = extract_text_from_pdf('Examples/RECO/EVANEOS - RECOMMANDATION 2025.pdf')
    pages = text.split('--- Page')
    
    print(f"Nombre total de pages: {len(pages)-1}")
    
    # Analyse des premières pages pour identifier la structure
    structure_analysis = []
    
    for i, page in enumerate(pages[1:21], 1):  # Analyse des 20 premières pages
        content = page.strip()
        if not content:
            continue
            
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        
        # Identification du type de slide
        slide_type = "Unknown"
        slide_title = ""
        slide_subtitle = ""
        slide_content = ""
        slide_layout = "Unknown"
        slide_data = {}
        
        # Analyse du contenu
        if len(lines) > 0:
            # Header systématique
            if 'evaneos revolvr recommendation 2024' in content.lower():
                slide_title = "EVANEOS REVOLVR RECOMMANDATION 2024"
                slide_subtitle = "KILLING IT SINCE 2010"
            
            # Navigation systématique
            if '1. brief reminder' in content.lower() and '2. brand overview' in content.lower():
                slide_data['navigation'] = True
            
            # Types de slides
            if 'résultats 2024' in content.lower():
                slide_type = "Results 2024"
                slide_layout = "Section Header"
                
            elif 'contexte' in content.lower():
                slide_type = "Context"
                slide_layout = "Section Header"
                
            elif 'stratégie 2025' in content.lower():
                slide_type = "Strategy 2025"
                slide_layout = "Section Header"
                
            elif 'new year, new me' in content.lower():
                slide_type = "Slogan"
                slide_layout = "Creative Display"
                slide_data['slogan'] = "New year, new me"
                
            elif 'move for good' in content.lower():
                slide_type = "Slogan"
                slide_layout = "Creative Display"
                slide_data['slogan'] = "Move for good"
                
            elif 'naturally different' in content.lower():
                slide_type = "Slogan"
                slide_layout = "Creative Display"
                slide_data['slogan'] = "Naturally different"
                
            elif 'family first' in content.lower():
                slide_type = "Slogan"
                slide_layout = "Creative Display"
                slide_data['slogan'] = "Family first"
                
            elif len(content) < 200 and 'evaneos' in content.lower():
                slide_type = "Cover"
                slide_layout = "Centered Minimal"
                
            else:
                slide_type = "Content"
                slide_layout = "Text + Visuals"
        
        # Extraction du contenu principal
        main_content = content[content.find('\n')+1:] if '\n' in content else content
        slide_content = main_content[:500]  # Premier 500 caractères
        
        structure_analysis.append({
            'slide': i,
            'type': slide_type,
            'title': slide_title,
            'subtitle': slide_subtitle,
            'layout': slide_layout,
            'content_preview': slide_content[:200] + '...' if len(slide_content) > 200 else slide_content,
            'data': slide_data,
            'word_count': len(content.split()),
            'has_navigation': 'navigation' in slide_data
        })
    
    # Compilation des statistiques
    stats = {
        'total_slides_analyzed': len(structure_analysis),
        'types_distribution': {},
        'layouts_distribution': {},
        'avg_word_count': sum(slide['word_count'] for slide in structure_analysis) / len(structure_analysis),
        'slides_with_navigation': sum(1 for slide in structure_analysis if slide['has_navigation']),
        'slogans_found': [slide['data'].get('slogan') for slide in structure_analysis if slide['data'].get('slogan')]
    }
    
    for slide in structure_analysis:
        slide_type = slide['type']
        slide_layout = slide['layout']
        stats['types_distribution'][slide_type] = stats['types_distribution'].get(slide_type, 0) + 1
        stats['layouts_distribution'][slide_layout] = stats['layouts_distribution'].get(slide_layout, 0) + 1
    
    print(f"\n=== STATISTIQUES EVANEOS ===")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    print(f"\n=== DÉTAIL DES SLIDES EVANEOS ===")
    for slide in structure_analysis:
        print(f"Slide {slide['slide']}: {slide['type']} - {slide['layout']}")
        print(f"  Content: {slide['content_preview'][:100]}...")
        print(f"  Data: {slide['data']}")
        print()
    
    return structure_analysis, stats

if __name__ == "__main__":
    analyze_evaneos_structure() 